import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from docker_deployment.commands import CommandResult
from docker_deployment.runner import run


class FakeCommandRunner:
    def __init__(self):
        self.commands = []

    def __call__(self, command, cwd=None, timeout=None):
        self.commands.append(list(command))
        if command == ["docker", "compose", "version"]:
            return CommandResult(0, "Docker Compose version", "")
        return CommandResult(0, "", "")


class HookTests(unittest.TestCase):
    def create_project(self):
        temporary_directory = tempfile.TemporaryDirectory()
        project_directory = Path(temporary_directory.name)
        (project_directory / "compose.yaml").write_text("services:\n  app:\n    image: example\n", encoding="utf-8")
        (project_directory / ".env").write_text(
            "APP_MODE=test\nGIT_COMMIT_SHA={0}\n".format("a" * 40),
            encoding="utf-8",
        )
        return temporary_directory, project_directory

    def make_config(self, project_directory):
        config = {
            "project_dir": str(project_directory),
            "compose_files": ["compose.yaml"],
            "env_file": ".env",
            "required_env": ["APP_MODE"],
            "deployment": {
                "commit_sha_env": "GIT_COMMIT_SHA",
                "state_file": ".deployment/current-sha",
            },
            "backup_paths": ["compose.yaml"],
            "compose": {
                "deploy_args": ["up", "-d"],
            },
            "health_checks": [
                {
                    "name": "Application health",
                    "type": "command",
                    "command": ["health-check"],
                    "retries": 1,
                    "interval": 0,
                }
            ],
            "rollback": {
                "command": ["rollback", "{backup_dir}"],
            },
            "hooks": {
                "backup_before_deploy": ["backup-hook"],
                "release_before_deploy": ["release-hook"],
            },
        }
        return config

    @patch("docker_deployment.preflight.shutil.which", return_value="docker")
    def test_hooks_run_before_backup_and_deploy(self, unused_which):
        temporary_directory, project_directory = self.create_project()
        self.addCleanup(temporary_directory.cleanup)
        command_runner = FakeCommandRunner()
        config = self.make_config(project_directory)

        exit_code = run(config, command_runner)

        self.assertEqual(exit_code, 0)
        self.assertTrue(any(command == ["backup-hook"] for command in command_runner.commands))
        self.assertTrue(any(command == ["release-hook"] for command in command_runner.commands))


if __name__ == "__main__":
    unittest.main()
