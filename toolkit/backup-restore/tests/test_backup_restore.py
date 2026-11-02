import tempfile
import unittest
from pathlib import Path

from backup_restore.backup import create_backup
from backup_restore.restore import restore_backup


class TestBackupRestore(unittest.TestCase):
    def test_create_and_restore_backup(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_directory = Path(temporary_directory) / "project"
            project_directory.mkdir()
            (project_directory / "app.txt").write_text("hello", encoding="utf-8")

            config = {
                "project_dir": str(project_directory),
                "backup_paths": ["app.txt"],
                "backup_dir": "backups",
            }

            backup_result = create_backup(config)
            self.assertTrue(backup_result["ok"])
            backup_dir = backup_result["backup_dir"]

            (project_directory / "app.txt").write_text("changed", encoding="utf-8")
            restore_result = restore_backup(config, backup_dir, confirm=True)
            self.assertTrue(restore_result["ok"])
            self.assertEqual(
                (project_directory / "app.txt").read_text(encoding="utf-8"), "hello"
            )

    def test_restore_requires_confirmation(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_directory = Path(temporary_directory) / "project"
            project_directory.mkdir()
            (project_directory / "app.txt").write_text("hello", encoding="utf-8")

            config = {
                "project_dir": str(project_directory),
                "backup_paths": ["app.txt"],
                "backup_dir": "backups",
            }
            backup_result = create_backup(config)
            restore_result = restore_backup(config, backup_result["backup_dir"], confirm=False)
            self.assertFalse(restore_result["ok"])


if __name__ == "__main__":
    unittest.main()
