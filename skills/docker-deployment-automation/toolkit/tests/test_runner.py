import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from docker_deployment.commands import CommandResult
from docker_deployment.runner import DeploymentRunner, run


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
        "deployment": {
            "commit_sha_env": "GIT_COMMIT_SHA",
            "state_file": ".deployment/current-sha",
        },
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
        (project_directory / ".env").write_text(
            "APP_MODE=test\nGIT_COMMIT_SHA={0}\n".format("a" * 40),
            encoding="utf-8",
        )
        return temporary_directory, project_directory

    def test_template_method_keeps_stage_order_for_a_subclass(self):
        temporary_directory, project_directory = self.create_project()
        self.addCleanup(temporary_directory.cleanup)

        class RecordingRunner(DeploymentRunner):
            def __init__(self, config):
                super().__init__(config)
                self.calls = []

            def initialize(self):
                super().initialize()
                self.calls.append("initialize")

            def preflight(self):
                self.calls.append("preflight")
                return {"ok": True, "errors": [], "compose_command": ["docker", "compose"]}

            def backup(self):
                self.calls.append("backup")
                return {"ok": True, "errors": [], "backup_dir": "backups/example"}

            def validate(self, compose_command):
                self.calls.append("validate")
                return {"ok": True, "error": ""}

            def deploy(self, compose_command):
                self.calls.append("deploy")
                return {"ok": True, "error": ""}

            def health_checks(self):
                self.calls.append("health_checks")
                return {"ok": True, "errors": []}

            def cleanup(self):
                self.calls.append("cleanup")
                return {"ok": True, "errors": []}

            def report(self):
                self.calls.append("report")

        runner = RecordingRunner(make_config(project_directory))

        exit_code = runner.run()

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            runner.calls,
            [
                "initialize",
                "preflight",
                "backup",
                "validate",
                "deploy",
                "health_checks",
                "cleanup",
                "report",
            ],
        )

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
        state_path = project_directory / ".deployment" / "current-sha"
        state_path.parent.mkdir()
        state_path.write_text("b" * 40, encoding="utf-8")
        command_runner = FakeCommandRunner(fail_health_once=True)

        exit_code = run(make_config(project_directory), command_runner)

        self.assertNotEqual(exit_code, 0)
        self.assertTrue(any(command[0] == "rollback" for command in command_runner.commands))
        self.assertGreaterEqual(command_runner.health_failures, 1)
        self.assertEqual(state_path.read_text(encoding="utf-8").strip(), "b" * 40)

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

    @patch("docker_deployment.preflight.shutil.which", return_value="docker")
    def test_missing_commit_sha_stops_before_backup(self, unused_which):
        temporary_directory, project_directory = self.create_project()
        self.addCleanup(temporary_directory.cleanup)
        command_runner = FakeCommandRunner()
        config = make_config(project_directory)
        config["deployment"]["commit_sha_env"] = "MISSING_COMMIT_SHA"

        exit_code = run(config, command_runner)

        self.assertNotEqual(exit_code, 0)
        self.assertFalse(any(command[0] == "db-backup" for command in command_runner.commands))
        self.assertFalse(any("up" in command for command in command_runner.commands))

    @patch("docker_deployment.preflight.shutil.which", return_value="docker")
    def test_commit_sha_is_used_in_deployment_and_saved(self, unused_which):
        temporary_directory, project_directory = self.create_project()
        self.addCleanup(temporary_directory.cleanup)
        command_runner = FakeCommandRunner()
        config = make_config(project_directory)
        config["compose"]["deploy_args"] = [
            "--project-name",
            "example-{commit_sha}",
            "up",
            "-d",
        ]

        exit_code = run(config, command_runner)

        self.assertEqual(exit_code, 0)
        deploy_command = next(command for command in command_runner.commands if "up" in command)
        self.assertIn("example-{0}".format("a" * 40), deploy_command)
        state_path = project_directory / ".deployment" / "current-sha"
        self.assertEqual(state_path.read_text(encoding="utf-8").strip(), "a" * 40)

    @patch("docker_deployment.preflight.shutil.which", return_value="docker")
    def test_rollback_receives_the_previous_commit_sha(self, unused_which):
        temporary_directory, project_directory = self.create_project()
        self.addCleanup(temporary_directory.cleanup)
        state_path = project_directory / ".deployment" / "current-sha"
        state_path.parent.mkdir()
        state_path.write_text("b" * 40, encoding="utf-8")
        command_runner = FakeCommandRunner(fail_deployment=True)
        config = make_config(project_directory)
        config["rollback"]["command"] = [
            "rollback",
            "{previous_commit_sha}",
            "{backup_dir}",
        ]

        exit_code = run(config, command_runner)

        self.assertNotEqual(exit_code, 0)
        rollback_command = next(
            command for command in command_runner.commands if command[0] == "rollback"
        )
        self.assertEqual(rollback_command[1], "b" * 40)

    @patch("docker_deployment.preflight.shutil.which", return_value="docker")
    def test_required_previous_commit_sha_is_validated(self, unused_which):
        temporary_directory, project_directory = self.create_project()
        self.addCleanup(temporary_directory.cleanup)
        command_runner = FakeCommandRunner()
        config = make_config(project_directory)
        config["deployment"]["require_previous_sha"] = True

        exit_code = run(config, command_runner)

        self.assertNotEqual(exit_code, 0)
        self.assertFalse(any("up" in command for command in command_runner.commands))


if __name__ == "__main__":
    unittest.main()
