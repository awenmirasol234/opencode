import shutil
import subprocess

from .command_strings import (
    DEFAULT_COMPOSE_FILES,
    DOCKER_COMPOSE_COMMAND,
    DOCKER_COMPOSE_LEGACY_COMMAND,
    DOCKER_COMPOSE_LEGACY_VERSION_COMMAND,
    DOCKER_COMPOSE_VERSION_COMMAND,
)


class CommandResult:
    def __init__(self, returncode, stdout, stderr):
        self.returncode = returncode
        if not stdout:
            stdout = ""
        if not stderr:
            stderr = ""
        self.stdout = stdout
        self.stderr = stderr

    def ok(self):
        return self.returncode == 0


def run_command(command, cwd, timeout):
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
    except FileNotFoundError as error:
        return CommandResult(1, "", str(error))
    except subprocess.TimeoutExpired as error:
        error_output = error.stderr
        if not error_output:
            error_output = ""
        error_text = error.stdout
        if not error_text:
            error_text = ""
        message = error_output + " The command timed out."
        return CommandResult(1, error_text, message)
    return CommandResult(completed.returncode, completed.stdout, completed.stderr)


def find_compose_command(run_command, project_dir):
    if shutil.which("docker"):
        result = run_command(DOCKER_COMPOSE_VERSION_COMMAND, project_dir, 30)
        if result.ok():
            return list(DOCKER_COMPOSE_COMMAND)
    if shutil.which("docker-compose"):
        result = run_command(DOCKER_COMPOSE_LEGACY_VERSION_COMMAND, project_dir, 30)
        if result.ok():
            return list(DOCKER_COMPOSE_LEGACY_COMMAND)
    return None


def format_command(command, values):
    items = []
    for item in command:
        text = str(item)
        for name in values:
            text = text.replace("{" + name + "}", str(values[name]))
        items.append(text)
    return items


def compose_arguments(config, compose_command, arguments):
    command = list(compose_command)
    for compose_file in config.get("compose_files", DEFAULT_COMPOSE_FILES):
        command.extend(["-f", str(compose_file)])
    env_file = config.get("env_file")
    if env_file:
        command.extend(["--env-file", str(env_file)])
    command.extend(arguments)
    return command
