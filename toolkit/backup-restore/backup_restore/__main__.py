import argparse
import importlib.util
from pathlib import Path

from .backup import create_backup
from .commands import run_command
from .restore import list_backups, restore_backup, verify_backup


def load_config(path):
    config_path = Path(path).resolve()
    spec = importlib.util.spec_from_file_location("backup_config", str(config_path))
    if spec is None or spec.loader is None:
        raise ValueError("The configuration file could not be loaded.")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    config = getattr(module, "CONFIG", None)
    if config is None and hasattr(module, "get_config"):
        config = module.get_config()
    if not isinstance(config, dict):
        raise ValueError("The configuration file must define a CONFIG dictionary.")
    return config


def main():
    parser = argparse.ArgumentParser(description="Back up or restore a Docker Compose project.")
    parser.add_argument("action", choices=["backup", "restore", "list", "verify"])
    parser.add_argument("--config", default="backup_config.py")
    parser.add_argument("--backup-dir")
    parser.add_argument("--yes", action="store_true")
    arguments = parser.parse_args()

    try:
        config = load_config(arguments.config)
    except Exception as error:
        print("The backup configuration could not be loaded: {0}".format(error))
        return 2

    if arguments.action == "backup":
        result = create_backup(config, run_command)
        if not result["ok"]:
            for error in result["errors"]:
                print(error)
            return 1
        print("Backup created at {0}.".format(result["backup_dir"]))
        return 0

    if arguments.action == "list":
        result = list_backups(config)
        if not result["ok"]:
            for error in result["errors"]:
                print(error)
            return 1
        for backup in result["backups"]:
            print(backup)
        return 0

    if arguments.action == "verify":
        backup_dir = arguments.backup_dir or config.get("backup_dir", "backups")
        result = verify_backup(config, backup_dir)
        if not result["ok"]:
            for error in result["errors"]:
                print(error)
            return 1
        print("The backup is valid.")
        return 0

    backup_dir = arguments.backup_dir
    if not backup_dir:
        backups = list_backups(config)
        if backups["ok"] and backups["backups"]:
            backup_dir = backups["backups"][-1]
        else:
            print("A backup directory is required.")
            return 2
    result = restore_backup(config, backup_dir, run_command, confirm=arguments.yes)
    if not result["ok"]:
        for error in result["errors"]:
            print(error)
        return 1
    print("Restore completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
