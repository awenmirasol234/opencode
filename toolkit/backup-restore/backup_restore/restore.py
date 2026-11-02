import shutil

from .commands import format_command
from .config import project_directory, project_path, validate_config


def restore_backup(config, backup_dir, command_runner=None, confirm=False):
    errors = validate_config(config)
    if errors:
        return {"ok": False, "errors": errors}

    if command_runner is None:
        from .commands import run_command

        command_runner = run_command

    if not confirm:
        return {
            "ok": False,
            "errors": ["Restore requires confirmation. Use --yes to continue."],
        }

    project_dir = project_directory(config)
    backup_path = project_path(config, backup_dir)
    if not backup_path.exists() or not backup_path.is_dir():
        return {"ok": False, "errors": ["The backup directory was not found."]}

    errors = []
    for source in backup_path.rglob("*"):
        if source.is_dir():
            continue
        relative_path = source.relative_to(backup_path)
        destination = project_dir / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(source, destination)
        except OSError as error:
            errors.append("The restore failed for {0}: {1}.".format(relative_path, error))

    database = config.get("database", {})
    restore_command = database.get("restore_command")
    top_level_restore = config.get("restore", {})
    if restore_command is None and isinstance(top_level_restore, dict):
        restore_command = top_level_restore.get("command")

    if restore_command:
        backup_file = database.get("backup_file", "database.backup")
        backup_file_path = (backup_path / backup_file).resolve()
        values = {
            "backup_dir": str(backup_path),
            "backup_file": str(backup_file_path),
            "project_dir": str(project_dir),
        }
        command = format_command(restore_command, values)
        result = command_runner(command, str(project_dir), 300)
        if not result.ok():
            errors.append("The database restore command failed.")

    if errors:
        return {"ok": False, "errors": errors}

    return {"ok": True, "errors": []}


def list_backups(config):
    errors = validate_config(config)
    if errors:
        return {"ok": False, "errors": errors, "backups": []}

    from .commands import find_backup_directories

    backups = [str(path) for path in find_backup_directories(config)]
    return {"ok": True, "errors": [], "backups": backups}


def verify_backup(config, backup_dir):
    errors = validate_config(config)
    if errors:
        return {"ok": False, "errors": errors}

    from .config import project_path

    backup_path = project_path(config, backup_dir)
    if not backup_path.exists() or not backup_path.is_dir():
        return {"ok": False, "errors": ["The backup directory was not found."]}

    if not any(backup_path.iterdir()):
        return {"ok": False, "errors": ["The backup directory is empty."]}

    return {"ok": True, "errors": []}
