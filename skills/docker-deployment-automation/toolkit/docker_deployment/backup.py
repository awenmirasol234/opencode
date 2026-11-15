import filecmp
import shutil
import time
from datetime import datetime

from .commands import compose_arguments
from .config import project_directory, project_path, section, setting


def create_backup_directory(config):
    root = project_path(config, setting(config, "backup_dir"))
    root.mkdir(parents=True, exist_ok=True)
    name = datetime.now().strftime("backup_%Y%m%d_%H%M%S")
    folder = root / name
    counter = 1
    while folder.exists():
        folder = root / "{0}_{1}".format(name, counter)
        counter += 1
    folder.mkdir()
    return folder


def verify_copy(source, target):
    if source.is_dir():
        for item in source.rglob("*"):
            copied = target / item.relative_to(source)
            if item.is_dir():
                if not copied.is_dir():
                    return False
                continue
            if not copied.is_file():
                return False
            if not filecmp.cmp(item, copied, shallow=False):
                return False
        return True
    if not target.is_file():
        return False
    return filecmp.cmp(source, target, shallow=False)


def copy_backup_paths(config, backup_dir, errors):
    project_dir = project_directory(config)
    for value in setting(config, "backup_paths"):
        source = project_dir / value
        if not source.exists():
            errors.append("The backup path was not found: {0}.".format(value))
            continue
        target = backup_dir / value
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)
        if not verify_copy(source, target):
            errors.append("The backup copy was not verified: {0}.".format(value))


def start_database_services(config, command_runner, errors):
    database = section(config, "database")
    services = database.get("services")
    if not services:
        return
    compose_command = config.get("compose_command")
    if not compose_command:
        errors.append("The Docker Compose command is missing.")
        return
    arguments = list(database.get("start_args"))
    arguments.extend(services)
    command = compose_arguments(config, compose_command, arguments)
    result = command_runner(command, str(project_directory(config)), 600)
    if not result.ok():
        errors.append("The database services could not be started.")


def wait_for_database_ready(config, command_runner, errors):
    database = section(config, "database")
    readiness_command = database.get("readiness_command")
    if not readiness_command:
        return
    timeout = database.get("readiness_timeout")
    interval = database.get("readiness_interval")
    retries = database.get("readiness_retries")
    deadline = time.monotonic() + timeout
    attempts = 0
    while True:
        result = command_runner(readiness_command, str(project_directory(config)), 60)
        if result.ok():
            return
        attempts += 1
        if attempts >= retries:
            break
        if time.monotonic() >= deadline:
            break
        time.sleep(interval)
    errors.append("The database was not ready in time.")


def run_database_backup(config, command_runner, backup_dir, errors):
    database = section(config, "database")
    backup_command = database.get("backup_command")
    if not backup_command:
        return
    backup_file = backup_dir / database.get("backup_file")
    values = {
        "backup_dir": str(backup_dir),
        "backup_file": str(backup_file),
        "project_dir": str(project_directory(config)),
    }
    command = []
    for item in backup_command:
        text = str(item)
        for name in values:
            text = text.replace("{" + name + "}", str(values[name]))
        command.append(text)
    result = command_runner(command, str(project_directory(config)), 600)
    if not result.ok():
        errors.append("The database backup command failed.")
        return
    if not backup_file.exists():
        errors.append("The database backup file was not created.")
        return
    if backup_file.stat().st_size == 0:
        errors.append("The database backup file is empty.")


def create_backups(config, command_runner, logger):
    logger.info("Creating the backup.")
    errors = []
    backup_dir = create_backup_directory(config)
    copy_backup_paths(config, backup_dir, errors)
    start_database_services(config, command_runner, errors)
    wait_for_database_ready(config, command_runner, errors)
    run_database_backup(config, command_runner, backup_dir, errors)
    if errors:
        success = False
    else:
        success = True
    result = {"ok": success, "errors": errors, "backup_dir": str(backup_dir)}
    if result["ok"]:
        logger.ok("The backup was created at {0}.".format(backup_dir))
    else:
        for error in errors:
            logger.fail(error)
    return result
