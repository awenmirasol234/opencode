import unittest

from docker_deployment.config_yaml import normalize_config


class NormalizeConfigTests(unittest.TestCase):
    def test_yaml_sections_become_the_runner_configuration(self):
        config = normalize_config(
            {
                "project_dir": "/srv/app",
                "env_file": ".env",
                "compose_files": ["compose.yaml", "compose.override.yaml"],
                "required_env": ["APP_ENV"],
                "required_images": ["example:latest"],
                "deployment": {
                    "commit_sha_env": "SHA",
                    "state_file": ".deploy/sha",
                    "require_previous_sha": True,
                },
                "locks": {"enabled": False, "file": ".deploy/lock"},
                "backup": {"enabled": False, "dir": "old-backups", "paths": ["data"]},
                "directories": {
                    "log_dir": "old-logs",
                    "protected_paths": ["data"],
                    "temp_paths": ["tmp"],
                },
                "services": {
                    "database": {
                        "services": ["db"],
                        "readiness_command": ["ready"],
                        "backup_command": ["dump", "{backup_file}"],
                        "backup_file": "db.sql",
                    }
                },
                "health": {
                    "timeout": 30,
                    "interval": 2,
                    "checks": [{"name": "app", "type": "command", "command": ["check"]}],
                },
                "rollback": {"command": ["undo"]},
                "compose": {"pull_args": [], "deploy_args": ["up", "-d"]},
                "hooks": {"backup_before_deploy": ["hook"]},
                "cleanup": {"enabled": False},
            }
        )

        self.assertEqual(config["project_dir"], "/srv/app")
        self.assertEqual(config["compose_files"], ["compose.yaml", "compose.override.yaml"])
        self.assertEqual(config["required_env"], ["APP_ENV"])
        self.assertEqual(config["required_images"], ["example:latest"])
        self.assertEqual(config["deployment"]["commit_sha_env"], "SHA")
        self.assertEqual(config["deployment"]["require_previous_sha"], True)
        self.assertEqual(config["deployment_lock"], False)
        self.assertEqual(config["lock_file"], ".deploy/lock")
        self.assertEqual(config["backup_enabled"], False)
        self.assertEqual(config["backup_dir"], "old-backups")
        self.assertEqual(config["backup_paths"], ["data"])
        self.assertEqual(config["log_dir"], "old-logs")
        self.assertEqual(config["protected_paths"], ["data"])
        self.assertEqual(config["temporary_paths"], ["tmp"])
        self.assertEqual(config["database"]["services"], ["db"])
        self.assertEqual(config["database"]["readiness_command"], ["ready"])
        self.assertEqual(config["database"]["backup_file"], "db.sql")
        self.assertEqual(config["health"]["timeout"], 30)
        self.assertEqual(config["health"]["interval"], 2)
        self.assertEqual(config["health_checks"][0]["name"], "app")
        self.assertEqual(config["rollback"]["command"], ["undo"])
        self.assertEqual(config["compose"]["pull_args"], [])
        self.assertEqual(config["hooks"]["backup_before_deploy"], ["hook"])
        self.assertEqual(config["cleanup_enabled"], False)

    def test_missing_sections_use_safe_defaults(self):
        config = normalize_config({})

        self.assertEqual(config["project_dir"], ".")
        self.assertEqual(config["env_file"], ".env")
        self.assertEqual(config["compose_files"], ["compose.yaml"])
        self.assertEqual(config["required_env"], [])
        self.assertEqual(config["required_images"], [])
        self.assertEqual(config["deployment"]["state_file"], ".deployment/current-sha")
        self.assertEqual(config["deployment_lock"], True)
        self.assertEqual(config["backup_enabled"], True)
        self.assertEqual(config["backup_dir"], "backups")
        self.assertEqual(config["health"]["timeout"], 120)
        self.assertEqual(config["health"]["interval"], 5)
        self.assertEqual(config["health_checks"], [])
        self.assertEqual(config["compose"]["deploy_args"], ["up", "-d"])
        self.assertEqual(config["cleanup_enabled"], True)


if __name__ == "__main__":
    unittest.main()
