import tempfile
import unittest
from pathlib import Path

from docker_deployment.commands import CommandResult
from docker_deployment.logger import Logger
from docker_deployment.preflight import run_preflight


class PreflightTests(unittest.TestCase):
    def test_missing_project_does_not_raise_when_disk_space_is_configured(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root_directory = Path(temporary_directory)
            logger = Logger(root_directory / "logs" / "preflight.log")

            def command_runner(command, cwd=None, timeout=None):
                return CommandResult(1, "", "Unavailable")

            result = run_preflight(
                {
                    "project_dir": str(root_directory / "missing"),
                    "compose_files": ["compose.yaml"],
                    "minimum_free_space_mb": 100,
                    "deployment": {
                        "commit_sha_env": "GIT_COMMIT_SHA",
                        "state_file": ".deployment/current-sha",
                    },
                },
                command_runner,
                logger,
            )

            logger.close()

        self.assertFalse(result["ok"])
        self.assertIn("The project directory was not found.", result["errors"])


if __name__ == "__main__":
    unittest.main()
