import shutil
import subprocess
from pathlib import Path


class CommandResult:
    def __init__(self, returncode, stdout, stderr):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

    def ok(self):
        return self.returncode == 0


def run_command(command, cwd=None, timeout=None):
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            shell=False,
            timeout=timeout,
            check=False,
        )
        return CommandResult(
            completed.returncode,
            completed.stdout or "",
            completed.stderr or "",
        )
    except FileNotFoundError as error:
        return CommandResult(127, "", str(error))
    except subprocess.TimeoutExpired as error:
        output = error.stdout or ""
        error_output = error.stderr or ""
        return CommandResult(124, output, error_output + " The command timed out.")


def format_command(command, values):
    formatted = []
    for item in command:
        formatted.append(str(item).format(**values))
    return formatted


def find_backup_directories(config):
    from .config import project_path

    backup_root = project_path(config, config.get("backup_dir", "backups"))
    if not backup_root.exists():
        return []
    return sorted(
        path for path in backup_root.iterdir() if path.is_dir()
    )
