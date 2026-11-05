CONFIG = {
    "project_dir": ".",
    "compose_files": ["compose.yaml"],
    "env_file": ".env",
    "required_env": ["APP_ENV"],
    "lock_file": ".deployment/deployment.lock",
    "deployment": {
        "commit_sha_env": "GIT_COMMIT_SHA",
        "state_file": ".deployment/current-sha",
        "require_previous_sha": False,
    },
    "backup_paths": ["compose.yaml", ".env.example"],
    "backup_dir": "backups",
    "log_dir": "logs",
    "temporary_paths": [".deployment-tmp"],
    "protected_paths": ["data"],
    "minimum_free_space_mb": 100,
    "required_services": [],
    "compose": {
        "deploy_args": ["up", "-d"],
    },
    "database": {
        # Add project-specific commands only when a database is used.
        # "readiness_command": ["replace", "with", "your", "readiness", "command"],
        # "backup_command": ["replace", "with", "your", "backup", "command", "{backup_file}"],
        # "backup_file": "database.backup",
        "readiness_retries": 30,
        "readiness_interval": 2,
        # Use readiness_timeout instead of retries for a time-based limit.
        # "readiness_timeout": 60,
    },
    "health": {
        "timeout": 120,
        "interval": 5,
    },
    "health_checks": [
        {
            "name": "Replace with the application health check",
            "type": "url",
            "url": "http://127.0.0.1:8080/health",
            "expected_status": 200,
        }
    ],
    "rollback": {
        # Replace this with a project-specific recovery command.
        "command": ["python", "scripts/rollback.py", "{backup_dir}"],
    },
    "hooks": {
        # Optional commands from the backup and release toolkits.
        # "backup_before_deploy": ["backup-restore", "backup", "--config", "backup_config.py"],
        # "release_before_deploy": ["release", "tag", "--config", "release_config.py"],
        # "restore_on_failure": ["backup-restore", "restore", "--config", "backup_config.py", "--backup-dir", "{backup_dir}", "--yes"],
        # "release_rollback_on_failure": ["release", "rollback-tag", "--config", "release_config.py", "--version", "{commit_sha}"],
    },
}
