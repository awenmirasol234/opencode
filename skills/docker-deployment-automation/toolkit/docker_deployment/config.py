import os
import re
import tempfile
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

    # Ignore blank lines and comments in the environment file.
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

    # Environment variables take priority over values in the file.
    for name in config.get("required_env", []):
        if name in os.environ:
            values[name] = os.environ[name]
    return values


def _valid_commit_sha(value):
    if not isinstance(value, str):
        return False
    return COMMIT_SHA_PATTERN.fullmatch(value.strip().lower()) is not None


def _path_inside_project(config, path):
    # State files must not write outside the project.
    project_dir = project_directory(config)
    try:
        path.relative_to(project_dir)
    except ValueError:
        return False
    return True


def read_deployment_identity(config):
    deployment = config.get("deployment")
    if not isinstance(deployment, dict):
        return {
            "ok": False,
            "errors": ["Deployment commit SHA configuration is missing."],
        }

    commit_sha_env = deployment.get("commit_sha_env", "GIT_COMMIT_SHA")
    if not isinstance(commit_sha_env, str) or not commit_sha_env.strip():
        return {
            "ok": False,
            "errors": ["The deployment commit SHA environment name is invalid."],
        }

    values = environment_values(config)
    commit_sha = os.environ.get(commit_sha_env, values.get(commit_sha_env, ""))
    commit_sha = commit_sha.strip().lower()
    if not _valid_commit_sha(commit_sha):
        return {
            "ok": False,
            "errors": [
                "The deployment commit SHA is missing or is not a full 40-character SHA."
            ],
        }

    state_file = deployment.get("state_file", ".deployment/current-sha")
    if not isinstance(state_file, str) or not state_file.strip():
        return {
            "ok": False,
            "errors": ["The deployment commit SHA state file is invalid."],
        }
    state_path = project_path(config, state_file)
    if not _path_inside_project(config, state_path):
        return {
            "ok": False,
            "errors": ["The deployment commit SHA state file must stay inside the project."],
        }

    previous_commit_sha = ""
    if state_path.exists():
        try:
            previous_commit_sha = state_path.read_text(encoding="utf-8").strip().lower()
        except OSError:
            return {
                "ok": False,
                "errors": ["The previous deployment commit SHA could not be read."],
            }
        if not _valid_commit_sha(previous_commit_sha):
            return {
                "ok": False,
                "errors": ["The previous deployment commit SHA is invalid."],
            }
    elif deployment.get("require_previous_sha", False):
        return {
            "ok": False,
            "errors": ["The previous deployment commit SHA was not found."],
        }

    return {
        "ok": True,
        "errors": [],
        "commit_sha": commit_sha,
        "previous_commit_sha": previous_commit_sha,
        "state_path": state_path,
    }


def save_deployment_identity(identity):
    if not identity:
        return {"ok": True, "error": ""}

    state_path = identity.get("state_path")
    commit_sha = identity.get("commit_sha", "")
    if state_path is None or not _valid_commit_sha(commit_sha):
        return {"ok": False, "error": "The deployment commit SHA could not be saved."}

    temporary_path = None
    try:
        # Write a complete file before replacing the current state.
        state_path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=".{0}.".format(state_path.name),
            dir=str(state_path.parent),
            text=True,
        )
        temporary_path = Path(temporary_name)
        with os.fdopen(descriptor, "w", encoding="utf-8") as state_file:
            state_file.write(commit_sha + "\n")
        os.replace(str(temporary_path), str(state_path))
        temporary_path = None
    except OSError:
        return {"ok": False, "error": "The deployment commit SHA could not be saved."}
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except OSError:
                pass

    return {"ok": True, "error": ""}
