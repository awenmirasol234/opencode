from .commands import format_command
from .config import project_directory
from .health import run_health_checks


def rollback(
    config,
    backup_result,
    command_runner,
    logger,
    deployment_identity=None,
):
    logger.info("Rolling back the application.")
    rollback_config = config.get("rollback", {})
    command = rollback_config.get("command")
    if not command:
        command = config.get("compose", {}).get("rollback_args")
    if not command:
        logger.fail("No rollback command was configured.")
        return {"ok": False, "error": "No rollback command was configured."}

    values = {
        "backup_dir": backup_result.get("backup_dir", ""),
        "project_dir": str(project_directory(config)),
    }
    if deployment_identity:
        values["commit_sha"] = deployment_identity.get("commit_sha", "")
        values["previous_commit_sha"] = deployment_identity.get("previous_commit_sha", "")
    command = format_command(command, values)
    result = command_runner(command, str(project_directory(config)), 600)
    if not result.ok():
        logger.fail("The application rollback failed.")
        return {"ok": False, "error": "The application rollback failed."}

    health_result = run_health_checks(config, command_runner, logger)
    if not health_result["ok"]:
        logger.fail("Rollback verification failed.")
        return {"ok": False, "error": "Rollback verification failed."}

    logger.success("Rollback completed and was verified successfully.")
    return {"ok": True, "error": ""}
