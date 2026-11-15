import os

from .command_strings import (
    DEFAULT_COMPOSE_FILES,
    DOCKER_IMAGE_INSPECT_COMMAND,
    DOCKER_INFO_COMMAND,
)
from .config import environment_values, project_directory


def check_project_directory(config, logger):
    if project_directory(config).is_dir():
        logger.ok("The project directory was found.")
        return ""
    logger.fail("The project directory was not found.")
    return "The project directory was not found."


def check_compose_files(config, logger):
    project_dir = project_directory(config)
    for compose_file in config.get("compose_files", DEFAULT_COMPOSE_FILES):
        path = project_dir / compose_file
        if not path.is_file():
            logger.fail("The Compose file was not found: {0}.".format(compose_file))
            return "The Compose file was not found: {0}.".format(compose_file)
    logger.ok("The Compose files were found.")
    return ""


def check_env_file(config, logger):
    env_file = config.get("env_file")
    if not env_file:
        return ""
    path = project_directory(config) / env_file
    if not path.is_file():
        logger.fail("The environment file was not found: {0}.".format(env_file))
        return "The environment file was not found: {0}.".format(env_file)
    logger.ok("The environment file was found.")
    return ""


def check_required_env(config, logger):
    values = environment_values(config)
    for name in config.get("required_env", []):
        if not values.get(name):
            logger.fail("The required environment value is missing: {0}.".format(name))
            return "The required environment value is missing: {0}.".format(name)
    logger.ok("The required environment values are available.")
    return ""


def check_project_permissions(config, logger):
    project_dir = project_directory(config)
    if not os.access(str(project_dir), os.R_OK):
        logger.fail("The project directory is not readable.")
        return "The project directory is not readable."
    if not os.access(str(project_dir), os.W_OK):
        logger.fail("The project directory is not writable.")
        return "The project directory is not writable."
    logger.ok("The project directory is readable and writable.")
    return ""


def check_deployment_identity(config, logger):
    identity = config.get("deployment_identity")
    if identity is None:
        return ""
    if not identity.get("ok"):
        logger.fail("The deployment commit SHA is not valid.")
        return "The deployment commit SHA is not valid."
    deployment = config.get("deployment", {})
    if deployment.get("require_previous_sha") and not identity.get("previous_commit_sha"):
        logger.fail("The previous deployment commit SHA is not available.")
        return "The previous deployment commit SHA is not available."
    logger.ok("The deployment commit SHA is valid.")
    return ""


def check_docker_available(config, logger):
    if config.get("compose_command"):
        logger.ok("Docker Compose is available.")
        return ""
    logger.fail("Docker Compose is not available.")
    return "Docker Compose is not available."


def check_docker_engine(config, command_runner, logger):
    result = command_runner(DOCKER_INFO_COMMAND, str(project_directory(config)), 60)
    if result.ok():
        logger.ok("The Docker Engine is available.")
        return ""
    logger.fail("The Docker Engine is not available.")
    return "The Docker Engine is not available."


def check_required_images(config, command_runner, logger):
    for image in config.get("required_images", []):
        if not isinstance(image, str) or not image.strip():
            logger.fail("A required Docker image name is not valid.")
            return "A required Docker image name is not valid."
        result = command_runner(
            DOCKER_IMAGE_INSPECT_COMMAND + [image], str(project_directory(config)), 60
        )
        if not result.ok():
            logger.fail("The required Docker image is not available: {0}.".format(image))
            return "The required Docker image is not available: {0}.".format(image)
    logger.ok("The required Docker images are available.")
    return ""


def run_preflight(config, command_runner, logger):
    logger.info("Running the preflight checks.")
    messages = [
        check_project_directory(config, logger),
        check_compose_files(config, logger),
        check_env_file(config, logger),
        check_required_env(config, logger),
        check_project_permissions(config, logger),
        check_deployment_identity(config, logger),
        check_docker_available(config, logger),
        check_docker_engine(config, command_runner, logger),
        check_required_images(config, command_runner, logger),
    ]
    errors = []
    for message in messages:
        if message:
            errors.append(message)
    if errors:
        success = False
    else:
        success = True
    result = {
        "ok": success,
        "errors": errors,
        "compose_command": config.get("compose_command"),
        "deployment_identity": config.get("deployment_identity"),
    }
    if result["ok"]:
        logger.ok("The preflight checks completed successfully.")
    else:
        logger.fail("The preflight checks failed.")
    return result
