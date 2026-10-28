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


def read_environment_file(path):
    values = {}
    if not path or not path.exists():
        return values

    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text or text.startswith("#") or "=" not in text:
            continue
        name, value = text.split("=", 1)
        name = name.strip()
        value = value.strip().strip('"').strip("'")
        if name:
            values[name] = value
    return values


def environment_values(config):
    values = {}
    env_file = config.get("env_file")
    if env_file:
        values.update(read_environment_file(project_path(config, env_file)))

    for name in config.get("required_env", []):
        if name in os.environ:
            values[name] = os.environ[name]
    return values
