from .commands import compose_arguments, format_command
from .config import project_directory


def validate_compose(config, compose_command, command_runner, logger):
    logger.info("Validating the Docker Compose configuration.")
    command = compose_arguments(config, compose_command, ["config"])
    result = command_runner(command, str(project_directory(config)), 120)
    if not result.ok():
        logger.fail("The Docker Compose configuration is not valid.")
        return {"ok": False, "error": "The Docker Compose configuration is not valid."}
    required_services = config.get("required_services", [])
    if required_services:
        command = compose_arguments(config, compose_command, ["config", "--services"])
        result = command_runner(command, str(project_directory(config)), 120)
        if not result.ok():
            logger.fail("The Docker Compose services could not be listed.")
            return {"ok": False, "error": "The Docker Compose services could not be listed."}
        services = result.stdout.split()
        for service in required_services:
            if service not in services:
                logger.fail("The required Compose service was not found: {0}.".format(service))
                return {"ok": False, "error": "The required Compose service was not found."}
    logger.ok("The Docker Compose configuration is valid.")
    return {"ok": True, "error": ""}


def pull_images(config, compose_command, command_runner, logger):
    pull_args = config.get("compose", {}).get("pull_args", ["pull"])
    if not pull_args:
        return {"ok": True, "error": ""}
    command = compose_arguments(config, compose_command, pull_args)
    result = command_runner(command, str(project_directory(config)), 600)
    if not result.ok():
        logger.fail("The application images could not be pulled.")
        return {"ok": False, "error": "The application images could not be pulled."}
    logger.ok("The application images were pulled.")
    return {"ok": True, "error": ""}


def deploy_application(config, compose_command, command_runner, logger, identity):
    logger.info("Deploying the application.")
    pull_result = pull_images(config, compose_command, command_runner, logger)
    if not pull_result["ok"]:
        return pull_result
    deploy_args = config.get("compose", {}).get("deploy_args", ["up", "-d"])
    values = {
        "commit_sha": "",
        "previous_commit_sha": "",
        "backup_dir": "",
        "project_dir": str(project_directory(config)),
    }
    if identity:
        values["commit_sha"] = identity.get("commit_sha", "")
        values["previous_commit_sha"] = identity.get("previous_commit_sha", "")
    command = compose_arguments(config, compose_command, format_command(deploy_args, values))
    result = command_runner(command, str(project_directory(config)), 600)
    if not result.ok():
        logger.fail("The application deployment failed.")
        return {"ok": False, "error": "The application deployment failed."}
    logger.ok("The application deployment completed successfully.")
    return {"ok": True, "error": ""}
