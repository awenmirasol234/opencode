import tempfile
import unittest
from pathlib import Path

from release_management.version import bump, read_version


class TestReleaseManagement(unittest.TestCase):
    def test_bump_patch_version(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_directory = Path(temporary_directory)
            (project_directory / "VERSION").write_text("1.2.3\n", encoding="utf-8")
            config = {
                "project_dir": str(project_directory),
                "version_file": "VERSION",
            }

            result = bump(config, "patch")
            self.assertTrue(result["ok"])
            self.assertEqual(result["old_version"], "1.2.3")
            self.assertEqual(result["version"], "1.2.4")
            self.assertEqual(
                (project_directory / "VERSION").read_text(encoding="utf-8").strip(),
                "1.2.4",
            )

    def test_read_missing_version_file(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            config = {
                "project_dir": temporary_directory,
                "version_file": "VERSION",
            }
            result = read_version(config)
            self.assertFalse(result["ok"])


if __name__ == "__main__":
    unittest.main()
