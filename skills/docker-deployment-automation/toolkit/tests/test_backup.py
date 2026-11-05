import tempfile
import unittest
from pathlib import Path

from docker_deployment.backup import create_backups
from docker_deployment.commands import CommandResult
from docker_deployment.logger import Logger


class BackupTests(unittest.TestCase):
    def test_backup_verification_confirms_copied_contents(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_directory = Path(temporary_directory)
            source = project_directory / "compose.yaml"
            source.write_text("services:\n  app:\n    image: example\n", encoding="utf-8")
            source_text = source.read_text(encoding="utf-8")
            logger = Logger(project_directory / "logs" / "backup.log")

            def command_runner(command, cwd=None, timeout=None):
                return CommandResult(0, "", "")

            result = create_backups(
                {
                    "project_dir": str(project_directory),
                    "backup_paths": ["compose.yaml"],
                    "backup_dir": "backups",
                },
                command_runner,
                logger,
            )

            logger.close()
            backup_file = Path(result["backup_dir"]) / "compose.yaml"
            backup_text = backup_file.read_text(encoding="utf-8")

        self.assertTrue(result["ok"])
        self.assertEqual(backup_text, source_text)


if __name__ == "__main__":
    unittest.main()
