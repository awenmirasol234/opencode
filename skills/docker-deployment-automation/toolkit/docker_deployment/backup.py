import filecmp
import shutil
import time
from datetime import datetime

from .commands import format_command
from .config import path_inside_project, project_directory, project_path


def _safe_project_path(config, value):
    # Backups must stay inside the project.
    path = project_path(config, value)
    if not path_inside_project(config, path):
        return None
    return path


def _new_backup_directory(config):
    # Keep each run's backup separate from earlier backups.
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


def _verify_copy(source, destination):
    if source.is_dir():
        for source_path in source.rglob("*"):
            relative_path = source_path.relative_to(source)
            destination_path = destination / relative_path
            if source_path.is_dir():
                if not destination_path.is_dir():
                    return False
            elif not destination_path.is_file():
                return False
            elif not filecmp.cmp(source_path, destination_path, shallow=False):
                return False
        return True
    if not destination.is_file():
        return False
    return filecmp.cmp(source, destination, shallow=False)


def _wait_for_database(config, command_runner, logger):
    # The database must be ready before its backup is made.
    database = config.get("database", {})
    readiness_command = database.get("readiness_command")
    if not readiness_command:
        return {"ok": True, "error": ""}

    retries = database.get("readiness_retries", 30)
    interval = database.get("readiness_interval", 5)
    timeout = database.get("readiness_timeout")
    if timeout is None and "readiness_retries" not in database:
        timeout = 120
    if not isinstance(retries, int) or isinstance(retries, bool) or retries < 1:
        logger.fail("The database readiness retry count is invalid.")
        return {"ok": False, "error": "The database readiness retry count is invalid."}
    if not isinstance(interval, (int, float)) or isinstance(interval, bool) or interval < 0:
        logger.fail("The database readiness interval is invalid.")
        return {"ok": False, "error": "The database readiness interval is invalid."}
    if timeout is not None and (
        not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or timeout < 0
    ):
        logger.fail("The database readiness timeout is invalid.")
        return {"ok": False, "error": "The database readiness timeout is invalid."}
    logger.info("Waiting for the database to become ready.")
    last_error = "The database did not become ready."
    deadline = None
    if timeout is not None:
        deadline = time.monotonic() + timeout
    attempt = 0
    while True:
        result = command_runner(readiness_command, str(project_directory(config)), 60)
        if result.ok():
            logger.ok("The database is ready.")
            return {"ok": True, "error": ""}
        if result.stderr:
            last_error = result.stderr.strip()
        attempt += 1
        if deadline is not None:
            if time.monotonic() >= deadline:
                break
        elif attempt >= retries:
            break
        if deadline is not None:
            remaining = deadline - time.monotonic()
            time.sleep(min(interval, max(remaining, 0)))
        else:
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
            if _verify_copy(source, destination):
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
            if backup_file_path.is_file() and backup_file_path.stat().st_size > 0:
                logger.ok("The database backup was saved.")
            else:
                errors.append("The database backup file could not be verified.")
        else:
            errors.append("The database backup command failed.")

        verify_command = database.get("verify_command")
        if verify_command and backup_file_path.is_file():
            verify_values = {
                "backup_dir": str(backup_dir),
                "backup_file": str(backup_file_path),
                "project_dir": str(project_dir),
            }
            formatted_verify_command = format_command(verify_command, verify_values)
            verify_result = command_runner(formatted_verify_command, str(project_dir), 300)
            if verify_result.ok():
                logger.ok("The database backup integrity was verified.")
            else:
                errors.append("The database backup integrity check failed.")

    if errors:
        for error in errors:
            logger.fail(error)
        return {"ok": False, "errors": errors, "backup_dir": str(backup_dir)}

    logger.success("Backups were created at {0}.".format(backup_dir))
    return {"ok": True, "errors": [], "backup_dir": str(backup_dir)}
