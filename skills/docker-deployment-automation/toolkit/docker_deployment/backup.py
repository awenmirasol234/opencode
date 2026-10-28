import shutil
import time
from datetime import datetime

from .commands import format_command
from .config import project_directory, project_path


def _safe_project_path(config, value):
    path = project_path(config, value)
    project_dir = project_directory(config)
    try:
        path.relative_to(project_dir)
    except ValueError:
        return None
    return path


def _new_backup_directory(config):
    backup_root = project_path(config, config.get("backup_dir", "backups"))
    backup_root.mkdir(parents=True, exist_ok=True)
    name = datetime.now().strftime("backup_%Y%m%d_%H%M%S")
    backup_dir = backup_root / name
    counter = 1
    while backup_dir.exists():
        backup_dir = backup_root / (name + "_" + str(counter))
        counter += 1
    backup_dir.mkdir()
    return backup_dir


def _copy_path(source, project_dir, backup_dir):
    relative_path = source.relative_to(project_dir)
    destination = backup_dir / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination)
    else:
        shutil.copy2(source, destination)
    return destination


def _wait_for_database(config, command_runner, logger):
    database = config.get("database", {})
    readiness_command = database.get("readiness_command")
    if not readiness_command:
        return {"ok": True, "error": ""}

    retries = database.get("readiness_retries", 30)
    interval = database.get("readiness_interval", 2)
    if retries < 1:
        logger.fail("The database readiness retry count is invalid.")
        return {"ok": False, "error": "The database readiness retry count is invalid."}
    logger.info("Waiting for the database to become ready.")
    last_error = "The database did not become ready."
    for attempt in range(retries):
        result = command_runner(readiness_command, str(project_directory(config)), 60)
        if result.ok():
            logger.ok("The database is ready.")
            return {"ok": True, "error": ""}
        if result.stderr:
            last_error = result.stderr.strip()
        if attempt + 1 < retries:
            time.sleep(interval)

    logger.fail("The database did not become ready.")
    return {"ok": False, "error": last_error}


def create_backups(config, command_runner, logger):
    logger.info("Creating backups.")
    readiness = _wait_for_database(config, command_runner, logger)
    if not readiness["ok"]:
        return {"ok": False, "errors": [readiness["error"]], "backup_dir": None}

    backup_dir = _new_backup_directory(config)
    project_dir = project_directory(config)
    errors = []

    for value in config.get("backup_paths", []):
        source = _safe_project_path(config, value)
        if source is None:
            errors.append("The backup path is outside the project: {0}.".format(value))
            continue
        if not source.exists():
            errors.append("The backup path was not found: {0}.".format(value))
            continue
        try:
            destination = _copy_path(source, project_dir, backup_dir)
            if destination.exists():
                logger.ok("The backup was saved for {0}.".format(value))
            else:
                errors.append("The backup could not be verified: {0}.".format(value))
        except OSError as error:
            errors.append("The backup failed for {0}: {1}.".format(value, error))

    database = config.get("database", {})
    backup_command = database.get("backup_command")
    if backup_command:
        backup_file = database.get("backup_file", "database.backup")
        backup_file_path = (backup_dir / backup_file).resolve()
        try:
            backup_file_path.relative_to(backup_dir.resolve())
        except ValueError:
            error = "The database backup file must stay inside the backup directory."
            logger.fail(error)
            return {"ok": False, "errors": [error], "backup_dir": str(backup_dir)}
        values = {
            "backup_dir": str(backup_dir),
            "backup_file": str(backup_file_path),
            "project_dir": str(project_dir),
        }
        command = format_command(backup_command, values)
        result = command_runner(command, str(project_dir), 300)
        if result.ok():
            if backup_file_path.exists():
                logger.ok("The database backup was saved.")
            else:
                errors.append("The database backup file could not be verified.")
        else:
            errors.append("The database backup command failed.")

    if errors:
        for error in errors:
            logger.fail(error)
        return {"ok": False, "errors": errors, "backup_dir": str(backup_dir)}

    logger.success("Backups were created at {0}.".format(backup_dir))
    return {"ok": True, "errors": [], "backup_dir": str(backup_dir)}
