from datetime import date

from .config import project_directory, project_path, validate_config


def read_version(config):
    errors = validate_config(config)
    if errors:
        return {"ok": False, "errors": errors, "version": ""}

    path = project_path(config, config.get("version_file", "VERSION"))
    if not path.exists():
        return {"ok": False, "errors": ["The version file was not found."], "version": ""}

    try:
        version = path.read_text(encoding="utf-8").strip().splitlines()[0].strip()
    except (OSError, IndexError):
        return {"ok": False, "errors": ["The version could not be read."], "version": ""}

    if not version:
        return {"ok": False, "errors": ["The version file is empty."], "version": ""}

    return {"ok": True, "errors": [], "version": version, "path": path}


def bump_version(version, part="patch"):
    pieces = version.strip().split(".")
    if len(pieces) < 3:
        pieces = (pieces + ["0", "0", "0"])[:3]

    try:
        major = int(pieces[0])
        minor = int(pieces[1])
        patch = int(pieces[2])
    except ValueError:
        return None

    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "patch":
        patch += 1
    else:
        return None

    return "{0}.{1}.{2}".format(major, minor, patch)


def bump(config, part="patch", command_runner=None):
    result = read_version(config)
    if not result["ok"]:
        return result

    new_version = bump_version(result["version"], part)
    if new_version is None:
        return {"ok": False, "errors": ["The version format is not supported."], "version": ""}

    path = result["path"]
    try:
        path.write_text(new_version + "\n", encoding="utf-8")
    except OSError as error:
        return {"ok": False, "errors": ["The version file could not be written: {0}.".format(error)]}

    return {"ok": True, "errors": [], "old_version": result["version"], "version": new_version}


def write_changelog(config, version, command_runner=None):
    errors = validate_config(config)
    if errors:
        return {"ok": False, "errors": errors}

    if command_runner is None:
        from .commands import run_command

        command_runner = run_command

    project_dir = project_directory(config)
    path = project_path(config, config.get("changelog_file", "CHANGELOG.md"))
    today = date.today().isoformat()
    heading = "## [{0}] - {1}".format(version, today)

    commits = ""
    result = command_runner(["git", "log", "--pretty=format:- %s", "-n", "20"], str(project_dir), 60)
    if result.ok():
        commits = result.stdout.strip()

    lines = []
    if path.exists():
        lines = path.read_text(encoding="utf-8").splitlines()
    if heading not in lines:
        lines.insert(0, heading)
        lines.insert(1, "")
        if commits:
            lines.insert(2, commits)
            lines.insert(3, "")
        lines.insert(0, "# Changelog")
        lines.insert(1, "")

    try:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except OSError as error:
        return {"ok": False, "errors": ["The changelog could not be written: {0}.".format(error)]}

    return {"ok": True, "errors": []}
