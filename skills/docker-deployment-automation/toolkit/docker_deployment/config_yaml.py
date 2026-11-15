def section(data, name):
    value = data.get(name, {})
    if not isinstance(value, dict):
        return {}
    return value


def load_yaml_config(path_str):
    try:
        import yaml
    except ImportError:
        raise ValueError("PyYAML is required to read YAML configuration files.")
    with open(path_str, "r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ValueError("The configuration file must contain a mapping.")
    return normalize_config(data)


def normalize_config(data):
    config = {}

    config["project_dir"] = data.get("project_dir", ".")
    config["env_file"] = data.get("env_file", ".env")
    config["compose_files"] = data.get("compose_files", ["compose.yaml"])
    config["required_env"] = data.get("required_env", [])
    config["required_images"] = data.get("required_images", [])
    config["required_services"] = data.get("required_services", [])

    deployment = section(data, "deployment")
    config["deployment"] = {
        "commit_sha_env": deployment.get("commit_sha_env", "GIT_COMMIT_SHA"),
        "state_file": deployment.get("state_file", ".deployment/current-sha"),
        "require_previous_sha": deployment.get("require_previous_sha", False),
    }

    locks = section(data, "locks")
    config["lock_file"] = locks.get("file", ".deployment/deployment.lock")
    config["deployment_lock"] = locks.get("enabled", True)

    backup = section(data, "backup")
    config["backup_dir"] = backup.get("dir", "backups")
    config["backup_paths"] = backup.get("paths", [])
    config["backup_enabled"] = backup.get("enabled", True)

    directories = section(data, "directories")
    config["log_dir"] = directories.get("log_dir", "logs")
    config["protected_paths"] = directories.get("protected_paths", [])
    config["temporary_paths"] = directories.get("temp_paths", [])

    services = section(data, "services")
    database = section(services, "database")
    config["database"] = {
        "services": database.get("services", []),
        "start_args": database.get("start_args", ["up", "-d"]),
        "readiness_command": database.get("readiness_command", []),
        "readiness_timeout": database.get("readiness_timeout", 60),
        "readiness_interval": database.get("readiness_interval", 5),
        "readiness_retries": database.get("readiness_retries", 30),
        "backup_command": database.get("backup_command", []),
        "backup_file": database.get("backup_file", "database.sql"),
    }

    health = section(data, "health")
    config["health"] = {
        "timeout": health.get("timeout", 120),
        "interval": health.get("interval", 5),
    }
    config["health_checks"] = health.get("checks", [])

    rollback = section(data, "rollback")
    config["rollback"] = {"command": rollback.get("command", [])}

    compose = section(data, "compose")
    config["compose"] = {
        "pull_args": compose.get("pull_args", ["pull"]),
        "deploy_args": compose.get("deploy_args", ["up", "-d"]),
        "rollback_args": compose.get("rollback_args", ["up", "-d"]),
    }

    config["hooks"] = section(data, "hooks")
    config["cleanup_enabled"] = section(data, "cleanup").get("enabled", True)

    return config
