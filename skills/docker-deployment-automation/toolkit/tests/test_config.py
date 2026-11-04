import tempfile
import unittest
from pathlib import Path

from docker_deployment.config import save_deployment_identity


class SaveDeploymentIdentityTests(unittest.TestCase):
    def test_writes_the_sha_and_leaves_no_temporary_file(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            state_path = Path(temporary_directory) / ".deployment" / "current-sha"
            identity = {"state_path": state_path, "commit_sha": "a" * 40}

            result = save_deployment_identity(identity)

            self.assertTrue(result["ok"])
            self.assertEqual(
                state_path.read_text(encoding="utf-8").strip(), "a" * 40
            )
            self.assertFalse(state_path.with_name(state_path.name + ".tmp").exists())
