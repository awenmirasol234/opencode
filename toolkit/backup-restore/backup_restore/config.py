import os
from pathlib import Path


def project_directory(config):
    value = config.get("project_dir", ".")
    return Path(value).expanduser().resolve()


def project_path(config, value):
    path = Path(value)
    if not path.is_absolute():
        path = project_directory(config) / path
    return path.resolve()


def is_command(value):
    return isinstance(value, list) and len(value) > 0 and all(
        isinstance(item, str) for item in value
    )


def validate_config(config):
    errors = []
    if not isinstance(config, dict):
        return ["The configuration must be a dictionary."]

    if not isinstance(config.get("backup_paths", []), list):
        errors.append("The backup_paths value must be a list.")

    backup_dir = config.get("backup_dir", "backups")
    if not isinstance(backup_dir, str) or not backup_dir.strip():
        errors.append("The backup_dir value must be a non-empty string.")

    database = config.get("database", {})
    if database and not isinstance(database, dict):
        errors.append("The database value must be a dictionary.")
    elif isinstance(database, dict):
        for key in ("readiness_command", "backup_command", "restore_command"):
            value = database.get(key)
            if value is not None and not is_command(value):
                errors.append("The database {0} value must be a command list.".format(key))

    restore = config.get("restore", {})
    if restore and not isinstance(restore, dict):
        errors.append("The restore value must be a dictionary.")
    elif isinstance(restore, dict):
        command = restore.get("command")
        if command is not None and not is_command(command):
            errors.append("The restore command value must be a command list.")

    return errors
