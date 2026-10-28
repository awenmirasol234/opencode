CONFIG = {
    "project_dir": ".",
    "compose_files": ["compose.yaml"],
    "env_file": ".env",
    "required_env": ["APP_ENV"],
    "backup_paths": ["compose.yaml", ".env.example"],
    "backup_dir": "backups",
    "log_dir": "logs",
    "temporary_paths": [".deployment-tmp"],
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
    },
    "health_checks": [
        {
            "name": "Replace with the application health check",
            "type": "url",
            "url": "http://127.0.0.1:8080/health",
            "expected_status": 200,
            "retries": 10,
            "interval": 3,
        }
    ],
    "rollback": {
        # Replace this with a project-specific recovery command.
        "command": ["python", "scripts/rollback.py", "{backup_dir}"],
    },
}
