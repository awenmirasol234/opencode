from datetime import datetime

from .backup import create_backups
from .cleanup import clean
from .commands import run_command
from .config import environment_values, project_directory, project_path
from .deployment import deploy, validate_compose
from .health import run_health_checks
from .logger import Logger
from .preflight import run_preflight
from .rollback import rollback


def _log_path(config):
    log_dir = project_path(config, config.get("log_dir", "logs"))
    log_dir.mkdir(parents=True, exist_ok=True)
    name = datetime.now().strftime("deployment_%Y%m%d_%H%M%S.log")
    path = log_dir / name
    counter = 1
    while path.exists():
        path = log_dir / "deployment_{0}_{1}.log".format(
            datetime.now().strftime("%Y%m%d_%H%M%S"), counter
        )
        counter += 1
    return path


def _report(logger, status, backup_result, rollback_result, cleanup_result, errors):
    logger.info("Deployment result: {0}.".format(status))
    if backup_result and backup_result.get("backup_dir"):
        logger.info("Backup location: {0}.".format(backup_result["backup_dir"]))
    if rollback_result:
        rollback_status = "failed"
        if rollback_result["ok"]:
            rollback_status = "successful"
        logger.info("Rollback result: {0}.".format(rollback_status))
    if cleanup_result:
        cleanup_status = "failed"
        if cleanup_result["ok"]:
            cleanup_status = "successful"
        logger.info("Cleanup result: {0}.".format(cleanup_status))
    for error in errors:
        logger.fail(error)


def _attempt_rollback(config, backup_result, command_runner, logger):
    try:
        return rollback(config, backup_result, command_runner, logger)
    except Exception as error:
        logger.fail("Rollback failed unexpectedly.")
        return {
            "ok": False,
            "error": "Rollback failed unexpectedly: {0}.".format(error),
        }


def run(config, command_runner=None):
    if command_runner is None:
        command_runner = run_command

    secret_values = list(environment_values(config).values())
    logger = Logger(_log_path(config), secret_values=secret_values)
    logger.info("Starting the Docker deployment.")

    backup_result = None
    rollback_result = None
    cleanup_result = None
    errors = []
    deployment_started = False
    status = "failed"

    try:
        preflight_result = run_preflight(config, command_runner, logger)
        if not preflight_result["ok"]:
            errors.extend(preflight_result["errors"])
        else:
            backup_result = create_backups(config, command_runner, logger)
            if not backup_result["ok"]:
                errors.extend(backup_result["errors"])
            else:
                compose_result = validate_compose(
                    config,
                    preflight_result["compose_command"],
                    command_runner,
                    logger,
                )
                if not compose_result["ok"]:
                    errors.append(compose_result["error"])
                else:
                    deployment_started = True
                    deploy_result = deploy(
                        config,
                        preflight_result["compose_command"],
                        command_runner,
                        logger,
                    )
                    if not deploy_result["ok"]:
                        errors.append(deploy_result["error"])
                        rollback_result = _attempt_rollback(
                            config, backup_result, command_runner, logger
                        )
                    else:
                        health_result = run_health_checks(config, command_runner, logger)
                        if not health_result["ok"]:
                            errors.extend(health_result["errors"])
                            rollback_result = _attempt_rollback(
                                config, backup_result, command_runner, logger
                            )
                        else:
                            status = "successful"
    except Exception as error:
        errors.append("An unexpected error occurred: {0}.".format(error))
        logger.fail("An unexpected error occurred during deployment.")
        if deployment_started:
            rollback_result = _attempt_rollback(
                config, backup_result or {}, command_runner, logger
            )

    try:
        cleanup_result = clean(config, logger)
        if not cleanup_result["ok"]:
            errors.extend(cleanup_result["errors"])
    except Exception as error:
        errors.append("Cleanup failed unexpectedly: {0}.".format(error))
        logger.fail("Cleanup failed unexpectedly.")

    if rollback_result and not rollback_result["ok"]:
        errors.append(rollback_result["error"])
    if errors:
        status = "failed"

    _report(logger, status, backup_result, rollback_result, cleanup_result, errors)
    logger.close()
    if status == "successful":
        return 0
    return 1
