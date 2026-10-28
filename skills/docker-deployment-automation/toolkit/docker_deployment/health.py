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

    logger.info("Running health checks.")
    errors = []
    for check in checks:
        name = check.get("name", "Application health")
        retries = check.get("retries", 3)
        interval = check.get("interval", 2)
        passed = False
        last_error = "The health check failed."
        for attempt in range(retries):
            passed, last_error = _run_check(check, command_runner, config)
            if passed:
                break
            if attempt + 1 < retries:
                time.sleep(interval)

        if passed:
            logger.ok("{0} passed.".format(name))
        else:
            error = "{0} failed: {1}".format(name, last_error)
            logger.fail(error)
            errors.append(error)

    if errors:
        logger.fail("Required health checks failed.")
        return {"ok": False, "errors": errors}

    logger.success("Health checks completed successfully.")
    return {"ok": True, "errors": []}
