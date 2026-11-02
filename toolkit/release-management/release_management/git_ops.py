from .commands import format_command
from .config import project_directory, project_path, validate_config


def tag_name(config, version):
    prefix = config.get("tag_prefix", "v")
    return "{0}{1}".format(prefix, version)


def create_tag(config, version, command_runner):
    errors = validate_config(config)
    if errors:
        return {"ok": False, "errors": errors}

    project_dir = project_directory(config)
    name = tag_name(config, version)
    result = command_runner(["git", "tag", name], str(project_dir), 60)
    if not result.ok():
        return {"ok": False, "errors": ["The Git tag could not be created: {0}.".format(result.stderr.strip())]}
    return {"ok": True, "errors": [], "tag": name}


def rollback_tag(config, version, command_runner, remote=False):
    errors = validate_config(config)
    if errors:
        return {"ok": False, "errors": errors}

    project_dir = project_directory(config)
    name = tag_name(config, version)
    result = command_runner(["git", "tag", "-d", name], str(project_dir), 60)
    if not result.ok():
        return {"ok": False, "errors": ["The Git tag could not be deleted: {0}.".format(result.stderr.strip())]}

    if remote:
        remote_name = config.get("remote", "origin")
        remote_result = command_runner(
            ["git", "push", remote_name, ":refs/tags/" + name],
            str(project_dir),
            60,
        )
        if not remote_result.ok():
            return {
                "ok": False,
                "errors": ["The remote Git tag could not be deleted: {0}.".format(remote_result.stderr.strip())],
            }

    return {"ok": True, "errors": [], "tag": name}


def write_release_notes(config, version, command_runner):
    errors = validate_config(config)
    if errors:
        return {"ok": False, "errors": errors}

    if command_runner is None:
        from .commands import run_command

        command_runner = run_command

    project_dir = project_directory(config)
    path = project_path(config, config.get("release_notes_file", "RELEASE_NOTES.md"))
    tag = tag_name(config, version)
    result = command_runner(["git", "log", "--pretty=format:- %s", "-n", "20"], str(project_dir), 60)
    commits = result.stdout.strip() if result.ok() else ""

    content = "# Release {0}\n\n".format(version)
    content += "Tag: {0}\n\n".format(tag)
    if commits:
        content += commits + "\n"

    try:
        path.write_text(content, encoding="utf-8")
    except OSError as error:
        return {"ok": False, "errors": ["The release notes could not be written: {0}.".format(error)]}

    return {"ok": True, "errors": [], "path": str(path)}
