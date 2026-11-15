from .commands import format_command
from .config import project_directory, section


def rollback_command_for(config):
    command = section(config, "rollback").get("command")
    if not command:
        command = section(config, "compose").get("rollback_args")
    return command


def perform_rollback(config, command_runner, logger, identity, backup_dir):
    command = rollback_command_for(config)
    if not command:
        logger.fail("No rollback command was configured.")
        return {"ok": False, "error": "No rollback command was configured."}
    if not backup_dir:
        backup_dir = ""
    values = {
        "backup_dir": str(backup_dir),
        "project_dir": str(project_directory(config)),
        "commit_sha": "",
        "previous_commit_sha": "",
    }
    if identity:
        values["commit_sha"] = identity.get("commit_sha", "")
        values["previous_commit_sha"] = identity.get("previous_commit_sha", "")
    command = format_command(command, values)
    result = command_runner(command, str(project_directory(config)), 600)
    if not result.ok():
        logger.fail("The application rollback failed.")
        return {"ok": False, "error": "The application rollback failed."}
    logger.ok("The application rollback completed successfully.")
    return {"ok": True, "error": ""}
