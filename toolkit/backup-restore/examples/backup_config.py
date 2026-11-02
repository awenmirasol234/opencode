CONFIG = {
    "project_dir": ".",
    "backup_paths": ["compose.yaml", ".env.example"],
    "backup_dir": "backups",
    "database": {
        # "readiness_command": ["replace", "with", "your", "readiness", "command"],
        # "backup_command": ["replace", "with", "your", "backup", "command", "{backup_file}"],
        # "backup_file": "database.backup",
        # "restore_command": ["replace", "with", "your", "restore", "command", "{backup_file}"],
    },
    "restore": {
        # "command": ["replace", "with", "your", "restore", "command", "{backup_dir}"],
    },
}
