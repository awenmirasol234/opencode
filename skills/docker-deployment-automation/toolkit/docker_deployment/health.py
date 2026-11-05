import time
from urllib.error import URLError
from urllib.request import urlopen

from .config import project_directory
from .deployment import build_compose_command


def _check_command(check, command_runner, config):
    command = check.get("command")
    if not command:
        return False, "The health-check command is missing.", True, ""
    timeout = check.get("timeout", 30)
    result = command_runner(command, str(project_directory(config)), timeout)
    if result.ok():
        return True, "", False, ""
    diagnostic = "\n".join(value for value in (result.stdout, result.stderr) if value)
    if result.stderr:
        return False, result.stderr.strip(), False, diagnostic
    return False, "The health-check command failed.", False, diagnostic


def _check_url(check):
    url = check.get("url")
    if not url:
        return False, "The health-check URL is missing.", True, ""
    timeout = check.get("timeout", 10)
    expected_status = check.get("expected_status", 200)
    try:
        with urlopen(url, timeout=timeout) as response:
            if response.status == expected_status:
                return True, "", False, ""
            return False, "The health-check returned an unexpected status.", False, ""
    except (OSError, URLError) as error:
        return False, str(error), False, ""


def _check_container(check, command_runner, config, compose_command):
    service = check.get("service")
    if not service:
        return False, "The container health-check service is missing.", True, ""
    if not compose_command:
        return False, "The Compose command is missing for the container health check.", True, ""

    ps_command = build_compose_command(config, compose_command, ["ps", "-q", service])
    ps_result = command_runner(ps_command, str(project_directory(config)), 60)
    container_id = ps_result.stdout.strip()
    if not ps_result.ok() or not container_id:
        diagnostic = "\n".join(value for value in (ps_result.stdout, ps_result.stderr) if value)
        return False, "The container is missing: {0}.".format(service), True, diagnostic

    container_id = container_id.splitlines()[0].strip()
    inspect_command = [
        "docker",
        "inspect",
        "--format",
        "{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{end}}",
        container_id,
    ]
    inspect_result = command_runner(inspect_command, str(project_directory(config)), 60)
    if not inspect_result.ok():
        diagnostic = "\n".join(
            value for value in (inspect_result.stdout, inspect_result.stderr) if value
        )
        return False, "The container status could not be read: {0}.".format(service), True, diagnostic

    status_text = inspect_result.stdout.strip()
    status_parts = status_text.split("|", 1)
    status = status_parts[0]
    health_status = ""
    if len(status_parts) == 2:
        health_status = status_parts[1]

    if status in ("exited", "dead"):
        return False, "The container is {0}: {1}.".format(status, service), True, status_text
    if status == "running" and health_status == "healthy":
        return True, "", False, ""
    if status == "running" and not health_status and not check.get("require_health", True):
        return True, "", False, ""
    if status == "running" and health_status == "unhealthy":
        return False, "The container is unhealthy: {0}.".format(service), False, status_text
    if status == "running" and health_status == "starting":
        return False, "The container health check is still starting: {0}.".format(service), False, status_text
    if status == "running" and not health_status:
        return False, "The container has no health check: {0}.".format(service), False, status_text
    return False, "The container is not running: {0}.".format(service), False, status_text


def _run_check(check, command_runner, config, compose_command):
    if not isinstance(check, dict):
        return False, "The health check configuration is invalid.", True, ""
    check_type = check.get("type", "command")
    if check_type == "command":
        return _check_command(check, command_runner, config)
    if check_type == "url":
        return _check_url(check)
    if check_type == "container":
        return _check_container(check, command_runner, config, compose_command)
    return False, "The health-check type is not supported.", True, ""


def _capture_diagnostics(checks, command_runner, config, compose_command):
    diagnostics = []
    for check in checks:
        if not isinstance(check, dict):
            continue
        if check.get("type", "command") != "container":
            continue
        service = check.get("service")
        if not service or not compose_command:
            continue
        command = build_compose_command(
            config,
            compose_command,
            ["logs", "--no-color", "--tail", "100", service],
        )
        result = command_runner(command, str(project_directory(config)), 60)
        output = "\n".join(value for value in (result.stdout, result.stderr) if value)
        if output:
            diagnostics.append("Diagnostics for {0}: {1}".format(service, output.strip()))
    return diagnostics


def run_health_checks(config, command_runner, logger, compose_command=None):
    checks = config.get("health_checks", [])
    if not checks:
        logger.warning("No health checks were configured.")
        return {"ok": False, "errors": ["No health checks were configured."], "diagnostics": []}

    health_config = config.get("health", {})
    if not isinstance(health_config, dict):
        logger.fail("The health-check configuration is invalid.")
        return {"ok": False, "errors": ["The health-check configuration is invalid."], "diagnostics": []}

    timeout = health_config.get("timeout", 120)
    interval = health_config.get("interval", 5)
    if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or timeout < 0:
        logger.fail("The health-check timeout is invalid.")
        return {"ok": False, "errors": ["The health-check timeout is invalid."], "diagnostics": []}
    if not isinstance(interval, (int, float)) or isinstance(interval, bool) or interval < 0:
        logger.fail("The health-check interval is invalid.")
        return {"ok": False, "errors": ["The health-check interval is invalid."], "diagnostics": []}

    logger.info(
        "Polling health checks for up to {0} seconds with a {1}-second interval.".format(
            timeout, interval
        )
    )
    deadline = time.monotonic() + timeout
    while True:
        errors = []
        warnings = []
        failed_checks = []
        diagnostics = []
        terminal_failure = False
        for check in checks:
            name = "Application health"
            required = True
            if isinstance(check, dict):
                name = check.get("name", name)
                required = check.get("required", True)
            passed, last_error, terminal, diagnostic = _run_check(
                check,
                command_runner,
                config,
                compose_command,
            )

            if passed:
                logger.ok("{0} passed.".format(name))
            else:
                error = "{0} failed: {1}".format(name, last_error)
                logger.warning(error)
                failed_checks.append(check)
                if diagnostic:
                    diagnostics.append("Output for {0}: {1}".format(name, diagnostic))
                if required:
                    errors.append(error)
                    if terminal:
                        terminal_failure = True
                else:
                    warnings.append(error)

        if not errors:
            for warning in warnings:
                logger.warning(warning)
            logger.success("Health checks completed successfully.")
            return {"ok": True, "errors": [], "warnings": warnings, "diagnostics": diagnostics}

        if terminal_failure or time.monotonic() >= deadline:
            diagnostics.extend(
                _capture_diagnostics(
                    failed_checks,
                    command_runner,
                    config,
                    compose_command,
                )
            )
            for diagnostic in diagnostics:
                logger.fail(diagnostic)
            logger.fail("Required health checks failed before the timeout.")
            return {"ok": False, "errors": errors, "diagnostics": diagnostics}

        if interval > 0:
            remaining = deadline - time.monotonic()
            time.sleep(min(interval, max(remaining, 0)))
