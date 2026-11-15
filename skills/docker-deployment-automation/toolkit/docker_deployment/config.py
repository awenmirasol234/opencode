import copy
import os
import re
from pathlib import Path

COMMIT_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")

DOCKER_COMPOSE_COMMAND = ["docker", "compose"]
DOCKER_COMPOSE_LEGACY_COMMAND = ["docker-compose"]
DOCKER_COMPOSE_VERSION_COMMAND = ["docker", "compose", "version"]
DOCKER_COMPOSE_LEGACY_VERSION_COMMAND = ["docker-compose", "version"]
DOCKER_INFO_COMMAND = ["docker", "info"]
DOCKER_IMAGE_INSPECT_COMMAND = ["docker", "image", "inspect"]
DOCKER_INSPECT_COMMAND = ["docker", "inspect"]
CONTAINER_INSPECT_FORMAT = "{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{end}}"

COMPOSE_PS_ARGS = ["ps", "-q"]
COMPOSE_VALIDATE_ARGS = ["config"]
COMPOSE_SERVICES_ARGS = ["config", "--services"]
COMPOSE_PULL_ARGS = ["pull"]
COMPOSE_START_ARGS = ["up", "-d"]
COMPOSE_DEPLOY_ARGS = ["up", "-d"]
COMPOSE_ROLLBACK_ARGS = ["up", "-d"]

DEFAULT_CONFIG = {
    "project_dir": ".",
    "env_file": ".env",
    "compose_files": ["compose.yaml"],
    "required_env": [],
    "required_images": [],
    "required_services": [],
    "deployment": {
        "commit_sha_env": "GIT_COMMIT_SHA",
        "state_file": ".deployment/current-sha",
        "require_previous_sha": False,
    },
    "lock_file": ".deployment/deployment.lock",
    "deployment_lock": True,
    "backup_dir": "backups",
    "backup_paths": [],
    "backup_enabled": True,
    "log_dir": "logs",
    "protected_paths": [],
    "temporary_paths": [],
    "cleanup_enabled": True,
    "rollback_enabled": True,
    "database": {
        "services": [],
        "start_args": ["up", "-d"],
        "readiness_command": [],
        "readiness_timeout": 60,
        "readiness_interval": 5,
        "readiness_retries": 30,
        "backup_command": [],
        "backup_file": "database.sql",
    },
    "health": {
        "timeout": 120,
        "interval": 5,
    },
    "health_checks": [],
    "compose": {
        "pull_args": ["pull"],
        "deploy_args": ["up", "-d"],
        "rollback_args": ["up", "-d"],
    },
    "rollback": {
        "command": [],
    },
    "hooks": {},
}


def setting(config, name):
    value = config.get(name)
    if value is None:
        value = DEFAULT_CONFIG.get(name)
    if isinstance(value, list):
        return list(value)
    return value


def section(config, name):
    values = copy.deepcopy(DEFAULT_CONFIG.get(name, {}))
    user_values = config.get(name, {})
    if isinstance(user_values, dict):
        values.update(user_values)
    return values


def project_directory(config):
    value = setting(config, "project_dir")
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
    env_file = setting(config, "env_file")
    if env_file:
        values.update(read_environment_file(project_path(config, env_file)))
    for name in setting(config, "required_env"):
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
