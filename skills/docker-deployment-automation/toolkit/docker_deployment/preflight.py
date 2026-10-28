import os
import shutil

from .commands import find_compose_command
from .config import environment_values, project_directory, project_path


def run_preflight(config, command_runner, logger):
    logger.info("Running preflight checks.")
    errors = []
    project_dir = project_directory(config)

    if project_dir.is_dir():
        logger.ok("The project directory was found.")
    else:
        errors.append("The project directory was not found.")
        logger.fail("The project directory was not found.")

    for compose_file in config.get("compose_files", ["compose.yaml"]):
        path = project_path(config, compose_file)
        if path.is_file():
            logger.ok("The Compose file was found.")
        else:
            errors.append("The Compose file was not found: {0}.".format(compose_file))
            logger.fail("The Compose file was not found: {0}.".format(compose_file))

    env_file = config.get("env_file")
    if env_file:
        path = project_path(config, env_file)
        if path.is_file():
            logger.ok("The environment file was found.")
        else:
            errors.append("The environment file was not found: {0}.".format(env_file))
            logger.fail("The environment file was not found: {0}.".format(env_file))

    values = environment_values(config)
    for name in config.get("required_env", []):
        if values.get(name):
            logger.ok("The required environment value {0} is available.".format(name))
        else:
            errors.append("The required environment value {0} is missing.".format(name))
            logger.fail("The required environment value {0} is missing.".format(name))

    if os.access(str(project_dir), os.R_OK):
        logger.ok("The project directory is readable.")
    else:
        errors.append("The project directory is not readable.")
        logger.fail("The project directory is not readable.")

    minimum_free_space = config.get("minimum_free_space_mb", 0)
    if minimum_free_space:
        usage = shutil.disk_usage(str(project_dir))
        available_mb = usage.free / (1024 * 1024)
        if available_mb >= minimum_free_space:
            logger.ok("The available disk space is sufficient.")
        else:
            errors.append("The available disk space is too low.")
            logger.fail("The available disk space is too low.")

    compose_command = find_compose_command(command_runner, str(project_dir))
    if compose_command:
        logger.ok("Docker Compose is available.")
    else:
        errors.append("Docker Compose is not available.")
        logger.fail("Docker Compose is not available.")

    if errors:
        logger.fail("Preflight checks failed.")
        return {"ok": False, "errors": errors, "compose_command": compose_command}

    logger.success("Preflight checks completed successfully.")
    return {"ok": True, "errors": [], "compose_command": compose_command}
