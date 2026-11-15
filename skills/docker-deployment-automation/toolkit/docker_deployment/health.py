import time
import urllib.error
import urllib.request

from .command_strings import (
    COMPOSE_PS_ARGS,
    CONTAINER_INSPECT_FORMAT,
    DOCKER_INSPECT_COMMAND,
)
from .config import project_directory


def check_command_type(check, command_runner, config):
    command = check.get("command")
    if not command:
        return {"passed": False, "error": "The health-check command is missing.", "terminal": True, "diagnostic": ""}
    timeout = check.get("timeout", 30)
    result = command_runner(command, str(project_directory(config)), timeout)
    if result.ok():
        return {"passed": True, "error": "", "terminal": False, "diagnostic": ""}
    diagnostic = "\n".join([result.stdout, result.stderr])
    if result.stderr:
        return {"passed": False, "error": result.stderr.strip(), "terminal": False, "diagnostic": diagnostic}
    return {"passed": False, "error": "The health-check command failed.", "terminal": False, "diagnostic": diagnostic}


def check_url_type(check):
    url = check.get("url")
    if not url:
        return {"passed": False, "error": "The health-check URL is missing.", "terminal": True, "diagnostic": ""}
    timeout = check.get("timeout", 10)
    expected_status = check.get("expected_status", 200)
    try:
        response = urllib.request.urlopen(url, timeout=timeout)
    except (OSError, urllib.error.URLError) as error:
        return {"passed": False, "error": str(error), "terminal": False, "diagnostic": ""}
    if response.status == expected_status:
        return {"passed": True, "error": "", "terminal": False, "diagnostic": ""}
    return {"passed": False, "error": "The health-check returned an unexpected status.", "terminal": False, "diagnostic": ""}


def find_container_id(check, command_runner, config, compose_command):
    service = check.get("service")
    command = list(compose_command) + COMPOSE_PS_ARGS + [service]
    result = command_runner(command, str(project_directory(config)), 30)
    if not result.ok():
        return ""
    parts = result.stdout.split()
    if not parts:
        return ""
    return parts[0]


def check_container_type(check, command_runner, config, compose_command):
    service = check.get("service")
    if not service:
        return {"passed": False, "error": "The container health-check service is missing.", "terminal": True, "diagnostic": ""}
    if not compose_command:
        return {"passed": False, "error": "The Docker Compose command is missing.", "terminal": True, "diagnostic": ""}
    container_id = find_container_id(check, command_runner, config, compose_command)
    if not container_id:
        return {"passed": False, "error": "The container was not found: {0}.".format(service), "terminal": True, "diagnostic": ""}
    command = DOCKER_INSPECT_COMMAND + ["--format", CONTAINER_INSPECT_FORMAT, container_id]
    result = command_runner(command, str(project_directory(config)), 30)
    if not result.ok():
        return {"passed": False, "error": "The container could not be inspected: {0}.".format(service), "terminal": True, "diagnostic": ""}
    output = result.stdout.strip()
    parts = output.split("|")
    status = parts[0].strip()
    health_status = ""
    if len(parts) > 1:
        health_status = parts[1].strip()
    if status in ("exited", "dead"):
        return {"passed": False, "error": "The container is {0}: {1}.".format(status, service), "terminal": True, "diagnostic": output}
    if status != "running":
        return {"passed": False, "error": "The container is not running: {0}.".format(service), "terminal": False, "diagnostic": output}
    if health_status == "healthy":
        return {"passed": True, "error": "", "terminal": False, "diagnostic": ""}
    if health_status == "unhealthy":
        return {"passed": False, "error": "The container is unhealthy: {0}.".format(service), "terminal": False, "diagnostic": output}
    if health_status == "starting":
        return {"passed": False, "error": "The container health check is still starting: {0}.".format(service), "terminal": False, "diagnostic": output}
    return {"passed": False, "error": "The container has no health check: {0}.".format(service), "terminal": False, "diagnostic": output}


def run_single_check(check, command_runner, config, compose_command):
    check_type = check.get("type", "command")
    if check_type == "command":
        return check_command_type(check, command_runner, config)
    if check_type == "url":
        return check_url_type(check)
    if check_type == "container":
        return check_container_type(check, command_runner, config, compose_command)
    return {"passed": False, "error": "The health-check type is not supported.", "terminal": True, "diagnostic": ""}


def run_health_checks(config, command_runner, logger, compose_command=None):
    checks = config.get("health_checks", [])
    health_config = config.get("health", {})
    timeout = health_config.get("timeout", 120)
    interval = health_config.get("interval", 5)
    deadline = time.monotonic() + timeout
    diagnostics = []
    errors = []
    while True:
        failed_checks = []
        for check in checks:
            if not isinstance(check, dict):
                continue
            result = run_single_check(check, command_runner, config, compose_command)
            name = check.get("name", "health check")
            if result["passed"]:
                logger.info("{0} passed.".format(name))
                continue
            error = "{0} failed: {1}".format(name, result["error"])
            if not check.get("required", True):
                logger.warn("{0} did not pass: {1}".format(name, result["error"]))
                continue
            logger.warn(error)
            failed_checks.append(check)
            if result["diagnostic"]:
                diagnostics.append("Output for {0}: {1}".format(name, result["diagnostic"]))
            if result["terminal"]:
                errors.append(error)
        if not failed_checks:
            return {"ok": True, "errors": [], "diagnostics": []}
        if errors:
            return {"ok": False, "errors": errors, "diagnostics": diagnostics}
        if time.monotonic() >= deadline:
            return {"ok": False, "errors": ["The health checks timed out."], "diagnostics": diagnostics}
        time.sleep(interval)
