import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from docker_deployment.commands import CommandResult
from docker_deployment.health import run_health_checks
from docker_deployment.logger import Logger


class ContainerCommandRunner:
    def __init__(self):
        self.commands = []
        self.inspect_count = 0

    def __call__(self, command, cwd=None, timeout=None):
        self.commands.append(list(command))
        if "ps" in command and "-q" in command:
            return CommandResult(0, "container-id\n", "")
        if command[:2] == ["docker", "inspect"]:
            self.inspect_count += 1
            if self.inspect_count == 1:
                return CommandResult(0, "running|starting\n", "")
            return CommandResult(0, "running|healthy\n", "")
        return CommandResult(0, "", "")


class HealthTests(unittest.TestCase):
    @patch("docker_deployment.health.time.sleep")
    def test_container_health_polls_until_healthy(self, health_sleep):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_directory = Path(temporary_directory)
            logger = Logger(project_directory / "logs" / "health.log")
            command_runner = ContainerCommandRunner()
            config = {
                "project_dir": str(project_directory),
                "compose_files": ["compose.yaml"],
                "health": {"timeout": 10, "interval": 2},
                "health_checks": [
                    {
                        "name": "Application container",
                        "type": "container",
                        "service": "app",
                    }
                ],
            }

            result = run_health_checks(
                config,
                command_runner,
                logger,
                ["docker", "compose"],
            )

            logger.close()

        self.assertTrue(result["ok"])
        self.assertEqual(command_runner.inspect_count, 2)
        health_sleep.assert_called_once_with(2)

    def test_exited_container_fails_without_waiting_for_timeout(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_directory = Path(temporary_directory)
            logger = Logger(project_directory / "logs" / "health.log")

            def command_runner(command, cwd=None, timeout=None):
                if command[:4] == ["docker", "compose", "ps", "-q"]:
                    return CommandResult(0, "container-id\n", "")
                return CommandResult(0, "exited|\n", "")

            config = {
                "project_dir": str(project_directory),
                "compose_files": ["compose.yaml"],
                "health": {"timeout": 120, "interval": 5},
                "health_checks": [
                    {
                        "name": "Application container",
                        "type": "container",
                        "service": "app",
                    }
                ],
            }

            result = run_health_checks(
                config,
                command_runner,
                logger,
                ["docker", "compose"],
            )

            logger.close()

        self.assertFalse(result["ok"])
        self.assertIn("exited", result["errors"][0])


if __name__ == "__main__":
    unittest.main()
