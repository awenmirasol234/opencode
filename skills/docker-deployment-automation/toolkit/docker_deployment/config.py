import os
import re
from pathlib import Path

COMMIT_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")


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
    for line in path.read_text(encoding="utf-8-sig").splitlines():
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


def is_valid_sha(value):
    if not isinstance(value, str):
        return False
    return COMMIT_SHA_PATTERN.fullmatch(value.strip().lower()) is not None


def read_previous_commit_sha(state_path):
    path = Path(state_path)
    if not path.exists():
        return ""
    try:
        value = path.read_text(encoding="utf-8").strip().lower()
    except OSError:
        return ""
    if is_valid_sha(value):
        return value
    return ""


def save_deployment_identity(identity):
    if not identity:
        return {"ok": True, "error": ""}
    state_path = identity.get("state_path")
    commit_sha = identity.get("commit_sha", "")
    if state_path is None or not is_valid_sha(commit_sha):
        return {"ok": False, "error": "The deployment commit SHA could not be saved."}
    path = Path(state_path)
    temporary_path = path.with_name(path.name + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path.write_text(commit_sha + "\n", encoding="utf-8")
        os.replace(str(temporary_path), str(path))
    except OSError:
        try:
            temporary_path.unlink()
        except OSError:
            pass
        return {"ok": False, "error": "The deployment commit SHA could not be saved."}
    return {"ok": True, "error": ""}
