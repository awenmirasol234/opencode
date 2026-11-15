from datetime import datetime

from .backup import create_backups
from .cleanup import clean
from .commands import find_compose_command, format_command, run_command
from .config import (
    environment_values,
    is_valid_sha,
    project_directory,
    project_path,
    read_previous_commit_sha,
    save_deployment_identity,
)
from .deployment import deploy_application, validate_compose
from .health import run_health_checks
from .lock import acquire_lock, release_lock
from .logger import Logger
from .preflight import run_preflight
from .rollback import perform_rollback


class DeploymentRunner:
    def __init__(self, config, command_runner=None):
        self.config = config
        self.command_runner = command_runner
        if self.command_runner is None:
            self.command_runner = run_command
        self.logger = None
        self.identity = None
        self.compose_command = None
        self.backup_dir = ""
        self.lock_result = {"ok": True, "error": ""}
        self.lock_acquired = False

    def log_path(self):
        log_dir = project_path(self.config, self.config.get("log_dir", "logs"))
        name = datetime.now().strftime("deployment_%Y%m%d_%H%M%S.log")
        path = log_dir / name
        counter = 1
        while path.exists():
            path = log_dir / "deployment_{0}_{1}.log".format(name, counter)
            counter += 1
        return path

    def initialize(self):
        env_values = environment_values(self.config)
        self.config["env_values"] = env_values
        deployment = self.config.get("deployment", {})
        commit_sha_env = deployment.get("commit_sha_env", "GIT_COMMIT_SHA")
        commit_sha = env_values.get(commit_sha_env, "")
        state_path = project_path(
            self.config, deployment.get("state_file", ".deployment/current-sha")
        )
        self.identity = {
            "ok": is_valid_sha(commit_sha),
            "commit_sha": commit_sha,
            "previous_commit_sha": read_previous_commit_sha(state_path),
            "state_path": state_path,
        }
        self.config["deployment_identity"] = self.identity
        self.logger = Logger(self.log_path(), None, list(env_values.values()))
        self.lock_result = acquire_lock(self.config)
        self.lock_acquired = False
        if self.lock_result["ok"]:
            if not self.lock_result.get("skipped", False):
                self.lock_acquired = True
        if not self.lock_result["ok"]:
            self.logger.fail(self.lock_result["error"])
        return self.lock_result

    def preflight(self):
        self.compose_command = find_compose_command(
            self.command_runner, str(project_directory(self.config))
        )
        self.config["compose_command"] = self.compose_command
        return run_preflight(self.config, self.command_runner, self.logger)

    def backup(self):
        if not self.config.get("backup_enabled", True):
            self.logger.info("The backup stage was disabled.")
            return {"ok": True, "errors": [], "backup_dir": ""}
        return create_backups(self.config, self.command_runner, self.logger)

    def validate(self, compose_command):
        return validate_compose(
            self.config, compose_command, self.command_runner, self.logger
        )

    def deploy(self, compose_command):
        return deploy_application(
            self.config, compose_command, self.command_runner, self.logger, self.identity
        )

    def health_checks(self):
        return run_health_checks(
            self.config, self.command_runner, self.logger, self.compose_command
        )

    def cleanup(self):
        if self.lock_acquired:
            release_lock(self.config)
            self.lock_acquired = False
        if not self.config.get("cleanup_enabled", True):
            self.logger.info("The cleanup stage was disabled.")
            return {"ok": True, "errors": []}
        return clean(self.config, self.logger)

    def report(self):
        self.logger.info("The deployment finished.")

    def rollback(self):
        if not self.config.get("rollback_enabled", True):
            self.logger.warn("The rollback stage was disabled.")
            return {"ok": True, "error": ""}
        self.run_hooks("restore_on_failure")
        result = perform_rollback(
            self.config,
            self.command_runner,
            self.logger,
            self.identity,
            self.backup_dir,
        )
        if not result["ok"]:
            self.logger.fail("The rollback failed.")
            return result
        self.run_hooks("release_rollback_on_failure")
        return result

    def run_hooks(self, hook_name):
        command = self.config.get("hooks", {}).get(hook_name)
        if not command:
            return True
        if not self.backup_dir:
            backup_dir_value = ""
        else:
            backup_dir_value = self.backup_dir
        values = {
            "backup_dir": str(backup_dir_value),
            "project_dir": str(project_directory(self.config)),
            "commit_sha": "",
            "previous_commit_sha": "",
        }
        if self.identity:
            values["commit_sha"] = self.identity.get("commit_sha", "")
            values["previous_commit_sha"] = self.identity.get("previous_commit_sha", "")
        command = format_command(command, values)
        result = self.command_runner(command, str(project_directory(self.config)), 300)
        if not result.ok():
            self.logger.fail("The hook failed: {0}.".format(hook_name))
            return False
        self.logger.ok("The hook completed: {0}.".format(hook_name))
        return True

    def execute(self):
        self.initialize()
        if not self.lock_result["ok"]:
            self.cleanup()
            self.report()
            return 1

        preflight_result = self.preflight()
        if not preflight_result.get("ok"):
            self.cleanup()
            self.report()
            return 1
        compose_command = preflight_result.get("compose_command")
        if not compose_command:
            compose_command = self.compose_command
        self.compose_command = compose_command

        if not self.run_hooks("backup_before_deploy"):
            self.cleanup()
            self.report()
            return 1

        backup_result = self.backup()
        self.backup_dir = backup_result.get("backup_dir", "")
        if not backup_result.get("ok"):
            self.cleanup()
            self.report()
            return 1

        validate_result = self.validate(self.compose_command)
        if not validate_result.get("ok"):
            self.cleanup()
            self.report()
            return 1

        if not self.run_hooks("release_before_deploy"):
            self.cleanup()
            self.report()
            return 1

        deploy_result = self.deploy(self.compose_command)
        if not deploy_result.get("ok"):
            self.rollback()
            self.cleanup()
            self.report()
            return 1

        health_result = self.health_checks()
        if not health_result.get("ok"):
            self.rollback()
            self.cleanup()
            self.report()
            return 1

        save_deployment_identity(self.identity)
        self.cleanup()
        self.report()
        return 0

    def run(self):
        try:
            return self.execute()
        finally:
            if self.logger:
                self.logger.close()


def run(config, command_runner=None):
    runner = DeploymentRunner(config, command_runner)
    return runner.run()
