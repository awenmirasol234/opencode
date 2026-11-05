import os
from datetime import datetime

from .config import path_inside_project, project_path


class DeploymentLock:
    def __init__(self, config):
        self.config = config
        value = config.get("lock_file", ".deployment/deployment.lock")
        self.path = None
        if isinstance(value, str) and value.strip():
            self.path = project_path(config, value)
        self.acquired = False

    def acquire(self):
        if self.path is None or not path_inside_project(self.config, self.path):
            return {
                "ok": False,
                "error": "The deployment lock file must stay inside the project.",
            }

        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            descriptor = os.open(
                str(self.path),
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                0o600,
            )
            with os.fdopen(descriptor, "w", encoding="utf-8") as lock_file:
                lock_file.write(
                    "process={0}\nstarted={1}\n".format(
                        os.getpid(), datetime.now().isoformat()
                    )
                )
            self.acquired = True
            return {"ok": True, "error": ""}
        except FileExistsError:
            return {
                "ok": False,
                "error": "Another deployment is already running.",
            }
        except OSError:
            return {
                "ok": False,
                "error": "The deployment lock could not be acquired.",
            }

    def release(self):
        if not self.acquired:
            return {"ok": True, "error": ""}

        try:
            self.path.unlink()
            self.acquired = False
            return {"ok": True, "error": ""}
        except OSError:
            return {
                "ok": False,
                "error": "The deployment lock could not be released.",
            }
