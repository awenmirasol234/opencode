import os
from datetime import datetime
from pathlib import Path

from .config import project_directory, project_path


def lock_file_path(config):
    value = config.get("lock_file", ".deployment/deployment.lock")
    return project_path(config, value)


def is_inside_project(path, config):
    try:
        Path(path).relative_to(project_directory(config))
        return True
    except ValueError:
        return False


def acquire_lock(config):
    if not config.get("deployment_lock", True):
        return {"ok": True, "error": "", "skipped": True}
    path = lock_file_path(config)
    if not is_inside_project(path, config):
        return {"ok": False, "error": "The deployment lock file must stay inside the project."}
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        handle = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        return {"ok": False, "error": "Another deployment is already running."}
    except OSError:
        return {"ok": False, "error": "The deployment lock could not be acquired."}
    with os.fdopen(handle, "w") as stream:
        stream.write("pid={0}\nstarted={1}\n".format(os.getpid(), datetime.now().isoformat()))
    return {"ok": True, "error": "", "skipped": False}


def release_lock(config):
    path = lock_file_path(config)
    try:
        path.unlink()
    except FileNotFoundError:
        return {"ok": True, "error": ""}
    except OSError:
        return {"ok": False, "error": "The deployment lock could not be released."}
    return {"ok": True, "error": ""}
