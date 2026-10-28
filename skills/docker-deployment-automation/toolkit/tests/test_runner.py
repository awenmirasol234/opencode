import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from docker_deployment.commands import CommandResult
from docker_deployment.runner import run


class FakeCommandRunner:
    def __init__(self, fail_deployment=False, fail_health_once=False, fail_config=False, fail_rollback=False):
        self.commands = []
        self.fail_deployment = fail_deployment
        self.fail_health_once = fail_health_once
        self.fail_config = fail_config
        self.fail_rollback = fail_rollback
        self.health_failures = 0

    def __call__(self, command, cwd=None, timeout=None):
        self.commands.append(list(command))

        if command == ["docker", "compose", "version"]:
            return CommandResult(0, "Docker Compose version", "")

        if command and command[0] == "health-check":
            if self.fail_health_once and self.health_failures == 0:
                self.health_failures += 1
                return CommandResult(1, "", "Health check failed")
            return CommandResult(0, "", "")

        if command and command[0] == "rollback":
            if self.fail_rollback:
                return CommandResult(1, "", "Rollback failed")
            return CommandResult(0, "Rollback completed", "")

        if command and command[0] == "db-backup":
            backup_file = command[1]
            Path(backup_file).write_text("database backup", encoding="utf-8")
            return CommandResult(0, "", "")

        if "config" in command:
            if self.fail_config:
                return CommandResult(1, "", "Compose configuration failed")
            if "--services" in command:
                return CommandResult(0, "app\n", "")
            return CommandResult(0, "name: example\n", "")

        if "up" in command and self.fail_deployment:
            return CommandResult(1, "", "Deployment failed")

        return CommandResult(0, "", "")


def make_config(project_directory):
    return {
        "project_dir": str(project_directory),
        "compose_files": ["compose.yaml"],
        "env_file": ".env",
        "required_env": ["APP_MODE"],
        "backup_paths": ["compose.yaml"],
        "compose": {
            "deploy_args": ["up", "-d"],
            "rollback_args": ["up", "-d"],
        },
        "rollback": {
            "command": ["rollback", "{backup_dir}"],
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
    }


class RunnerTests(unittest.TestCase):
    def create_project(self):
        temporary_directory = tempfile.TemporaryDirectory()
        project_directory = Path(temporary_directory.name)
        (project_directory / "compose.yaml").write_text("services:\n  app:\n    image: example\n", encoding="utf-8")
        (project_directory / ".env").write_text("APP_MODE=test\n", encoding="utf-8")
        return temporary_directory, project_directory

    @patch("docker_deployment.preflight.shutil.which", return_value="docker")
    def test_runs_stages_in_order(self, unused_which):
        temporary_directory, project_directory = self.create_project()
        self.addCleanup(temporary_directory.cleanup)
        command_runner = FakeCommandRunner()

        exit_code = run(make_config(project_directory), command_runner)

        self.assertEqual(exit_code, 0)
        config_index = next(index for index, command in enumerate(command_runner.commands) if "config" in command and "--services" not in command)
        deploy_index = next(index for index, command in enumerate(command_runner.commands) if "up" in command)
        health_index = next(index for index, command in enumerate(command_runner.commands) if command[0] == "health-check")
        self.assertLess(config_index, deploy_index)
        self.assertLess(deploy_index, health_index)

    @patch("docker_deployment.preflight.shutil.which", return_value="docker")
    def test_preflight_failure_does_not_deploy_or_rollback(self, unused_which):
        temporary_directory, project_directory = self.create_project()
        self.addCleanup(temporary_directory.cleanup)
        command_runner = FakeCommandRunner()
        config = make_config(project_directory)
        config["required_env"] = ["MISSING_VALUE"]

        exit_code = run(config, command_runner)

        self.assertNotEqual(exit_code, 0)
        self.assertFalse(any("up" in command for command in command_runner.commands))
        self.assertFalse(any(command[0] == "rollback" for command in command_runner.commands))

    @patch("docker_deployment.preflight.shutil.which", return_value="docker")
    def test_deployment_failure_triggers_rollback(self, unused_which):
        temporary_directory, project_directory = self.create_project()
        self.addCleanup(temporary_directory.cleanup)
        command_runner = FakeCommandRunner(fail_deployment=True)

        exit_code = run(make_config(project_directory), command_runner)

        self.assertNotEqual(exit_code, 0)
        self.assertTrue(any(command[0] == "rollback" for command in command_runner.commands))

    @patch("docker_deployment.preflight.shutil.which", return_value="docker")
    def test_health_failure_triggers_rollback(self, unused_which):
        temporary_directory, project_directory = self.create_project()
        self.addCleanup(temporary_directory.cleanup)
        command_runner = FakeCommandRunner(fail_health_once=True)

        exit_code = run(make_config(project_directory), command_runner)

        self.assertNotEqual(exit_code, 0)
        self.assertTrue(any(command[0] == "rollback" for command in command_runner.commands))
        self.assertGreaterEqual(command_runner.health_failures, 1)

    @patch("docker_deployment.preflight.shutil.which", return_value="docker")
    def test_backup_failure_does_not_trigger_rollback(self, unused_which):
        temporary_directory, project_directory = self.create_project()
        self.addCleanup(temporary_directory.cleanup)
        command_runner = FakeCommandRunner()
        config = make_config(project_directory)
        config["backup_paths"] = ["missing.yaml"]

        exit_code = run(config, command_runner)

        self.assertNotEqual(exit_code, 0)
        self.assertFalse(any(command[0] == "rollback" for command in command_runner.commands))

    @patch("docker_deployment.preflight.shutil.which", return_value="docker")
    def test_compose_validation_failure_does_not_trigger_rollback(self, unused_which):
        temporary_directory, project_directory = self.create_project()
        self.addCleanup(temporary_directory.cleanup)
        command_runner = FakeCommandRunner(fail_config=True)

        exit_code = run(make_config(project_directory), command_runner)

        self.assertNotEqual(exit_code, 0)
        self.assertFalse(any("up" in command for command in command_runner.commands))
        self.assertFalse(any(command[0] == "rollback" for command in command_runner.commands))

    @patch("docker_deployment.preflight.shutil.which", return_value="docker")
    def test_database_is_ready_before_database_backup(self, unused_which):
        temporary_directory, project_directory = self.create_project()
        self.addCleanup(temporary_directory.cleanup)
        command_runner = FakeCommandRunner()
        config = make_config(project_directory)
        config["database"] = {
            "readiness_command": ["db-ready"],
            "readiness_retries": 1,
            "readiness_interval": 0,
            "backup_command": ["db-backup", "{backup_file}"],
            "backup_file": "database.sql",
        }

        exit_code = run(config, command_runner)

        self.assertEqual(exit_code, 0)
        readiness_index = next(index for index, command in enumerate(command_runner.commands) if command[0] == "db-ready")
        backup_index = next(index for index, command in enumerate(command_runner.commands) if command[0] == "db-backup")
        self.assertLess(readiness_index, backup_index)

    @patch("docker_deployment.preflight.shutil.which", return_value="docker")
    def test_rollback_failure_returns_nonzero(self, unused_which):
        temporary_directory, project_directory = self.create_project()
        self.addCleanup(temporary_directory.cleanup)
        command_runner = FakeCommandRunner(fail_deployment=True, fail_rollback=True)

        exit_code = run(make_config(project_directory), command_runner)

        self.assertNotEqual(exit_code, 0)
        self.assertTrue(any(command[0] == "rollback" for command in command_runner.commands))


if __name__ == "__main__":
    unittest.main()
