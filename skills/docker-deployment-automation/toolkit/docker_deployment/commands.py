import shutil
import subprocess


class CommandResult:
    def __init__(self, returncode, stdout, stderr):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

    def ok(self):
        return self.returncode == 0


def run_command(command, cwd=None, timeout=None):
    # Run commands directly so config values are not passed through a shell.
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


def find_compose_command(command_runner, project_dir):
    # Support both current and older Docker Compose installs.
    docker_path = shutil.which("docker")
    if docker_path:
        result = command_runner(["docker", "compose", "version"], project_dir, 30)
        if result.ok():
            return ["docker", "compose"]

    compose_path = shutil.which("docker-compose")
    if compose_path:
        result = command_runner(["docker-compose", "version"], project_dir, 30)
        if result.ok():
            return ["docker-compose"]

    return None


def format_command(command, values):
    formatted = []
    for item in command:
        formatted.append(str(item).format(**values))
    return formatted
