import argparse
import importlib.util
from pathlib import Path

from .commands import run_command
from .config import validate_config
from .git_ops import create_tag, rollback_tag, write_release_notes
from .version import bump, read_version, write_changelog


def load_config(path):
    config_path = Path(path).resolve()
    spec = importlib.util.spec_from_file_location("release_config", str(config_path))
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
    parser = argparse.ArgumentParser(description="Manage project releases.")
    parser.add_argument(
        "action",
        choices=["bump", "changelog", "tag", "release-notes", "rollback-tag"],
    )
    parser.add_argument("--config", default="release_config.py")
    parser.add_argument("--part", choices=["major", "minor", "patch"], default="patch")
    parser.add_argument("--version")
    parser.add_argument("--remote", action="store_true")
    arguments = parser.parse_args()

    try:
        config = load_config(arguments.config)
    except Exception as error:
        print("The release configuration could not be loaded: {0}".format(error))
        return 2

    errors = validate_config(config)
    if errors:
        for error in errors:
            print(error)
        return 2

    if arguments.action == "bump":
        result = bump(config, arguments.part, run_command)
        if not result["ok"]:
            for error in result["errors"]:
                print(error)
            return 1
        print("Version changed from {0} to {1}.".format(result["old_version"], result["version"]))
        return 0

    version_result = read_version(config)
    if not version_result["ok"]:
        for error in version_result["errors"]:
            print(error)
        return 1
    version = arguments.version or version_result["version"]

    if arguments.action == "changelog":
        result = write_changelog(config, version, run_command)
    elif arguments.action == "tag":
        result = create_tag(config, version, run_command)
    elif arguments.action == "release-notes":
        result = write_release_notes(config, version, run_command)
    else:
        result = rollback_tag(config, version, run_command, remote=arguments.remote)

    if not result["ok"]:
        for error in result["errors"]:
            print(error)
        return 1

    if arguments.action == "tag":
        print("Created tag {0}.".format(result["tag"]))
    elif arguments.action == "rollback-tag":
        print("Deleted tag {0}.".format(result["tag"]))
    else:
        print("Release step completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
