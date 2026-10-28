import tempfile
import unittest
from pathlib import Path

from docker_deployment.cleanup import clean
from docker_deployment.logger import Logger


class CleanupTests(unittest.TestCase):
    def test_removes_temporary_path_but_preserves_backup_and_log_paths(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_directory = Path(temporary_directory)
            temporary_path = project_directory / "tmp" / "deployment.txt"
            backup_path = project_directory / "backups" / "backup.txt"
            log_path = project_directory / "logs" / "deployment.log"
            temporary_path.parent.mkdir()
            backup_path.parent.mkdir()
            log_path.parent.mkdir()
            temporary_path.write_text("temporary", encoding="utf-8")
            backup_path.write_text("backup", encoding="utf-8")
            log_path.write_text("log", encoding="utf-8")

            logger = Logger(project_directory / "logs" / "cleanup.log")
            result = clean(
                {
                    "project_dir": str(project_directory),
                    "temporary_paths": ["tmp/deployment.txt"],
                    "backup_dir": "backups",
                    "log_dir": "logs",
                },
                logger,
            )
            logger.close()

            self.assertTrue(result["ok"])
            self.assertFalse(temporary_path.exists())
            self.assertTrue(backup_path.exists())
            self.assertTrue(log_path.exists())

    def test_rejects_paths_outside_the_project(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_directory = Path(temporary_directory) / "project"
            project_directory.mkdir()
            logger = Logger(project_directory / "logs" / "cleanup.log")

            result = clean(
                {
                    "project_dir": str(project_directory),
                    "temporary_paths": ["../outside.txt"],
                    "backup_dir": "backups",
                    "log_dir": "logs",
                },
                logger,
            )
            logger.close()

        self.assertFalse(result["ok"])

    def test_rejects_the_project_directory(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_directory = Path(temporary_directory)
            logger = Logger(project_directory / "logs" / "cleanup.log")

            result = clean(
                {
                    "project_dir": str(project_directory),
                    "temporary_paths": ["."],
                },
                logger,
            )
            logger.close()

        self.assertFalse(result["ok"])


if __name__ == "__main__":
    unittest.main()
