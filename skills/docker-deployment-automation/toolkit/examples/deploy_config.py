# This example uses explicit command lists. Commands are never run through a shell.
CONFIG = {
    "project_dir": ".",
    "compose_files": ["compose.yaml"],
    "env_file": ".env",
    "required_env": ["APP_ENV"],
    # The runner creates this file atomically and removes it after cleanup.
    # Keep the lock enabled for normal deployments.
    "deployment_lock": True,
    "lock_file": ".deployment/deployment.lock",
    "backup_enabled": True,
    "rollback_enabled": True,
    "cleanup_enabled": True,
    "deployment": {
        "commit_sha_env": "GIT_COMMIT_SHA",
        "state_file": ".deployment/current-sha",
        "require_previous_sha": False,
    },
    "backup_paths": ["compose.yaml", ".env.example"],
    "backup_dir": "backups",
    "log_dir": "logs",
    "temporary_paths": [".deployment-tmp"],
    # Add host-mounted database or application data paths here.
    "protected_paths": ["data"],
    "minimum_free_space_mb": 100,
    # These images are checked during preflight. Compose pulls images again
    # before application startup when compose.pull_args is configured.
    "required_images": [],
    "required_services": [],
    "compose": {
        "pull_args": ["pull"],
        "deploy_args": ["up", "-d"],
    },
    "database": {
        # Add project-specific commands only when a database is used. Services
        # start before readiness polling and backup creation.
        # "services": ["db"],
        # "readiness_command": ["replace", "with", "your", "readiness", "command"],
        # "backup_command": ["replace", "with", "your", "backup", "command", "{backup_file}"],
        # "verify_command": ["replace", "with", "your", "backup", "verification", "command", "{backup_file}"],
        # "backup_file": "database.backup",
        # The default timeout is 120 seconds and the default interval is 5 seconds.
        "readiness_timeout": 120,
        "readiness_interval": 5,
    },
    "health": {
        # Health checks run immediately, then repeat until they pass or timeout.
        "timeout": 120,
        "interval": 5,
    },
    "health_checks": [
        {
            "name": "Replace with the application health check",
            "type": "url",
            "url": "http://127.0.0.1:8080/health",
            "expected_status": 200,
            # Container checks require a Docker healthcheck unless require_health is false.
            # Set required to False for a noncritical service.
            # "type": "container",
            # "service": "app",
            # "required": True,
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
