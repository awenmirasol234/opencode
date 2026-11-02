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

    for key in ("version_file", "changelog_file", "release_notes_file"):
        value = config.get(key)
        if value is not None and (not isinstance(value, str) or not value.strip()):
            errors.append("The {0} value must be a non-empty string.".format(key))

    tag_prefix = config.get("tag_prefix", "v")
    if not isinstance(tag_prefix, str):
        errors.append("The tag_prefix value must be a string.")

    for key in ("pre_bump_command", "post_tag_command"):
        value = config.get(key)
        if value is not None and not is_command(value):
            errors.append("The {0} value must be a command list.".format(key))

    return errors
