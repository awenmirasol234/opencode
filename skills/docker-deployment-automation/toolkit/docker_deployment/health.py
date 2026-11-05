import time
from urllib.error import URLError
from urllib.request import urlopen

from .config import project_directory


def _check_command(check, command_runner, config):
    command = check.get("command")
    if not command:
        return False, "The health-check command is missing."
    timeout = check.get("timeout", 30)
    result = command_runner(command, str(project_directory(config)), timeout)
    if result.ok():
        return True, ""
    if result.stderr:
        return False, result.stderr.strip()
    return False, "The health-check command failed."


def _check_url(check):
    url = check.get("url")
    if not url:
        return False, "The health-check URL is missing."
    timeout = check.get("timeout", 10)
    expected_status = check.get("expected_status", 200)
    try:
        with urlopen(url, timeout=timeout) as response:
            if response.status == expected_status:
                return True, ""
            return False, "The health-check returned an unexpected status."
    except (OSError, URLError) as error:
        return False, str(error)


def _run_check(check, command_runner, config):
    check_type = check.get("type", "command")
    if check_type == "command":
        return _check_command(check, command_runner, config)
    if check_type == "url":
        return _check_url(check)
    return False, "The health-check type is not supported."


def run_health_checks(config, command_runner, logger):
    checks = config.get("health_checks", [])
    if not checks:
        logger.warning("No health checks were configured.")
        return {"ok": False, "errors": ["No health checks were configured."]}

    health_config = config.get("health", {})
    if not isinstance(health_config, dict):
        logger.fail("The health-check configuration is invalid.")
        return {"ok": False, "errors": ["The health-check configuration is invalid."]}

    timeout = health_config.get("timeout", 120)
    interval = health_config.get("interval", 5)
    if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or timeout < 0:
        logger.fail("The health-check timeout is invalid.")
        return {"ok": False, "errors": ["The health-check timeout is invalid."]}
    if not isinstance(interval, (int, float)) or isinstance(interval, bool) or interval < 0:
        logger.fail("The health-check interval is invalid.")
        return {"ok": False, "errors": ["The health-check interval is invalid."]}

    logger.info(
        "Polling health checks for up to {0} seconds with a {1}-second interval.".format(
            timeout, interval
        )
    )
    deadline = time.monotonic() + timeout
    while True:
        errors = []
        for check in checks:
            name = check.get("name", "Application health")
            passed, last_error = _run_check(check, command_runner, config)

            if passed:
                logger.ok("{0} passed.".format(name))
            else:
                error = "{0} failed: {1}".format(name, last_error)
                logger.warning(error)
                errors.append(error)

        if not errors:
            logger.success("Health checks completed successfully.")
            return {"ok": True, "errors": []}

        if time.monotonic() >= deadline:
            logger.fail("Required health checks failed before the timeout.")
            return {"ok": False, "errors": errors}

        if interval > 0:
            remaining = deadline - time.monotonic()
            time.sleep(min(interval, max(remaining, 0)))
