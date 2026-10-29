from .commands import format_command
from .config import project_directory, project_path


def _compose_command(config, compose_command, arguments):
    command = list(compose_command)
    for compose_file in config.get("compose_files", ["compose.yaml"]):
        command.extend(["-f", str(project_path(config, compose_file))])

    env_file = config.get("env_file")
    if env_file:
        command.extend(["--env-file", str(project_path(config, env_file))])
    command.extend(arguments)
    return command


def validate_compose(config, compose_command, command_runner, logger):
    logger.info("Validating the Docker Compose configuration.")
    command = _compose_command(config, compose_command, ["config"])
    result = command_runner(command, str(project_directory(config)), 120)
    if not result.ok():
        logger.fail("Docker Compose validation failed.")
        return {"ok": False, "error": "Docker Compose validation failed."}

    required_services = config.get("required_services", [])
    if required_services:
        services_command = _compose_command(config, compose_command, ["config", "--services"])
        services_result = command_runner(services_command, str(project_directory(config)), 120)
        if not services_result.ok():
            logger.fail("The Docker Compose services could not be listed.")
            return {"ok": False, "error": "The Docker Compose services could not be listed."}
        services = services_result.stdout.split()
        for service in required_services:
            if service not in services:
                logger.fail("The required Compose service was not found: {0}.".format(service))
                return {"ok": False, "error": "A required Compose service was not found."}

    logger.success("Docker Compose validation completed successfully.")
    return {"ok": True, "error": ""}


def deploy(config, compose_command, command_runner, logger, deployment_identity=None):
    logger.info("Deploying the application.")
    arguments = config.get("compose", {}).get("deploy_args", ["up", "-d"])
    if deployment_identity:
        arguments = format_command(
            arguments,
            {
                "commit_sha": deployment_identity.get("commit_sha", ""),
                "previous_commit_sha": deployment_identity.get("previous_commit_sha", ""),
            },
        )
    command = _compose_command(config, compose_command, arguments)
    result = command_runner(command, str(project_directory(config)), 600)
    if not result.ok():
        logger.fail("The application deployment failed.")
        return {"ok": False, "error": "The application deployment failed."}

    logger.success("The application deployment completed successfully.")
    return {"ok": True, "error": ""}
