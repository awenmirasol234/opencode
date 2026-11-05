import os

from .commands import find_compose_command
from .config import (
    environment_values,
    project_directory,
    project_path,
    read_deployment_identity,
)


def run_preflight(config, command_runner, logger):
    # Do not change services until every required check passes.
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

    if os.access(str(project_dir), os.W_OK):
        logger.ok("The project directory is writable.")
    else:
        errors.append("The project directory is not writable.")
        logger.fail("The project directory is not writable.")

    identity_result = read_deployment_identity(config)
    deployment_identity = None
    if identity_result["ok"]:
        deployment_identity = identity_result
        logger.ok("The deployment commit SHA is valid.")
        if identity_result.get("previous_commit_sha"):
            logger.ok("The previous deployment commit SHA was found.")
        else:
            logger.warning("No previous deployment commit SHA was found.")
    else:
        for error in identity_result["errors"]:
            errors.append(error)
            logger.fail(error)

    compose_command = find_compose_command(command_runner, str(project_dir))
    if compose_command:
        logger.ok("Docker Compose is available.")
    else:
        errors.append("Docker Compose is not available.")
        logger.fail("Docker Compose is not available.")

    docker_result = command_runner(["docker", "info"], str(project_dir), 60)
    if docker_result.ok():
        logger.ok("The Docker Engine is available.")
    else:
        errors.append("The Docker Engine is not available.")
        logger.fail("The Docker Engine is not available.")

    for image in config.get("required_images", []):
        if not isinstance(image, str) or not image.strip():
            errors.append("A required Docker image name is invalid.")
            logger.fail("A required Docker image name is invalid.")
            continue
        image_result = command_runner(
            ["docker", "image", "inspect", image],
            str(project_dir),
            60,
        )
        if image_result.ok():
            logger.ok("The required Docker image is available: {0}.".format(image))
        else:
            errors.append("The required Docker image is not available: {0}.".format(image))
            logger.fail("The required Docker image is not available: {0}.".format(image))

    if errors:
        logger.fail("Preflight checks failed.")
        return {
            "ok": False,
            "errors": errors,
            "compose_command": compose_command,
            "deployment_identity": deployment_identity,
        }

    logger.success("Preflight checks completed successfully.")
    return {
        "ok": True,
        "errors": [],
        "compose_command": compose_command,
        "deployment_identity": deployment_identity,
    }
