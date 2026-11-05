import time
from datetime import datetime

from .backup import create_backups
from .cleanup import clean
from .commands import format_command, run_command
from .config import environment_values, project_directory, project_path, save_deployment_identity
from .deployment import deploy as deploy_application
from .deployment import start_database_services
from .deployment import validate_compose
from .health import run_health_checks
from .logger import Logger
from .lock import DeploymentLock
from .preflight import run_preflight
from .rollback import rollback as restore_rollback


def _log_path(config):
    # Choose a new name so previous logs are preserved.
    log_dir = project_path(config, config.get("log_dir", "logs"))
    log_dir.mkdir(parents=True, exist_ok=True)
    name = datetime.now().strftime("deployment_%Y%m%d_%H%M%S.log")
    path = log_dir / name
    counter = 1
    while path.exists():
        path = log_dir / "deployment_{0}_{1}.log".format(
            datetime.now().strftime("%Y%m%d_%H%M%S"), counter
        )
        counter += 1
    return path


class DeploymentRunner:
    def __init__(self, config, command_runner=None):
        self.config = config
        self.command_runner = command_runner or run_command
        self.logger = None
        self.backup_result = None
        self.rollback_result = None
        self.cleanup_result = None
        self.deployment_identity = None
        self.errors = []
        self.deployment_started = False
        self.status = "failed"
        self.lock = DeploymentLock(config)
        self.lock_result = None
        self.compose_command = None
        self.health_result = None
        self.diagnostics = []
        self.started_at = None

    def initialize(self):
        self.started_at = time.monotonic()
        environment = environment_values(self.config)
        secret_values = list(environment.values())
        deployment = self.config.get("deployment", {})
        if not isinstance(deployment, dict):
            deployment = {}
        commit_sha_env = deployment.get("commit_sha_env", "GIT_COMMIT_SHA")
        commit_sha = environment.get(commit_sha_env, "")
        if commit_sha:
            filtered_secret_values = []
            for value in secret_values:
                if value != commit_sha:
                    filtered_secret_values.append(value)
            secret_values = filtered_secret_values
        self.logger = Logger(_log_path(self.config), secret_values=secret_values)
        self.logger.info("Starting the Docker deployment.")

    def preflight(self):
        return run_preflight(self.config, self.command_runner, self.logger)

    def backup(self):
        return create_backups(self.config, self.command_runner, self.logger)

    def start_database(self):
        return start_database_services(
            self.config,
            self.compose_command,
            self.command_runner,
            self.logger,
        )

    def validate(self, compose_command):
        return validate_compose(
            self.config,
            compose_command,
            self.command_runner,
            self.logger,
        )

    def deploy(self, compose_command):
        return deploy_application(
            self.config,
            compose_command,
            self.command_runner,
            self.logger,
            self.deployment_identity,
        )

    def health_checks(self):
        self.health_result = run_health_checks(
            self.config,
            self.command_runner,
            self.logger,
            self.compose_command,
        )
        return self.health_result

    def rollback(self):
        return restore_rollback(
            self.config,
            self.backup_result or {},
            self.command_runner,
            self.logger,
            self.deployment_identity,
            self.compose_command,
        )

    def record_deployment_identity(self):
        return save_deployment_identity(self.deployment_identity)

    def cleanup(self):
        return clean(self.config, self.logger)

    def acquire_lock(self):
        if self.config.get("deployment_lock", True) is False:
            self.logger.warning("The deployment lock is disabled.")
            return {"ok": True, "error": "", "skipped": True}
        self.logger.info("Acquiring the deployment lock.")
        result = self.lock.acquire()
        if result["ok"]:
            self.logger.ok("The deployment lock was acquired.")
        else:
            self.logger.fail(result["error"])
        return result

    def release_lock(self):
        if self.lock_result and self.lock_result.get("skipped"):
            return {"ok": True, "error": "", "skipped": True}
        result = self.lock.release()
        if result["ok"]:
            self.logger.ok("The deployment lock was released.")
        else:
            self.logger.fail(result["error"])
        return result

    def report(self):
        self.logger.info("Deployment result: {0}.".format(self.status))
        if self.started_at is not None:
            duration = time.monotonic() - self.started_at
            self.logger.info("Deployment duration: {0:.2f} seconds.".format(duration))
        if self.deployment_identity:
            self.logger.info(
                "Current deployment SHA: {0}.".format(
                    self.deployment_identity.get("commit_sha", "")
                )
            )
            previous_sha = self.deployment_identity.get("previous_commit_sha", "")
            if previous_sha:
                self.logger.info("Previous deployment SHA: {0}.".format(previous_sha))
            else:
                self.logger.info("Previous deployment SHA: none.")
        if self.backup_result and self.backup_result.get("backup_dir"):
            self.logger.info("Backup location: {0}.".format(self.backup_result["backup_dir"]))
        if self.backup_result and self.backup_result.get("skipped"):
            self.logger.warning("Backups were skipped by configuration.")
        if self.rollback_result:
            rollback_status = "failed"
            if self.rollback_result.get("skipped"):
                rollback_status = "skipped"
            elif self.rollback_result["ok"]:
                rollback_status = "successful"
            self.logger.info("Rollback result: {0}.".format(rollback_status))
        if self.cleanup_result:
            cleanup_status = "failed"
            if self.cleanup_result.get("skipped"):
                cleanup_status = "skipped"
            elif self.cleanup_result["ok"]:
                cleanup_status = "successful"
            self.logger.info("Cleanup result: {0}.".format(cleanup_status))
        for error in self.errors:
            self.logger.fail(error)
        for diagnostic in self.diagnostics:
            self.logger.fail(diagnostic)

    def run_hook(self, name):
        hooks = self.config.get("hooks", {})
        command = hooks.get(name)
        if not command:
            return {"ok": True, "skipped": True, "error": ""}

        values = {
            "project_dir": str(project_directory(self.config)),
            "backup_dir": (self.backup_result or {}).get("backup_dir", ""),
            "commit_sha": "",
            "previous_commit_sha": "",
        }
        if self.deployment_identity:
            values["commit_sha"] = self.deployment_identity.get("commit_sha", "")
            values["previous_commit_sha"] = self.deployment_identity.get(
                "previous_commit_sha", ""
            )

        try:
            formatted = format_command(command, values)
            result = self.command_runner(formatted, str(project_directory(self.config)), 300)
            if not result.ok():
                error = "The {0} hook failed.".format(name)
                self.logger.fail(error)
                return {"ok": False, "error": error, "skipped": False}
            self.logger.ok("The {0} hook completed.".format(name))
            return {"ok": True, "error": "", "skipped": False}
        except Exception as error:
            message = "The {0} hook failed unexpectedly: {1}.".format(name, error)
            self.logger.fail(message)
            return {"ok": False, "error": message, "skipped": False}

    def attempt_recovery(self):
        if self.config.get("rollback_enabled", True) is False:
            self.logger.warning("Rollback is disabled.")
            return {"ok": True, "error": "", "skipped": True, "diagnostics": []}
        result = self.attempt_rollback()
        self.diagnostics.extend(result.get("diagnostics", []))
        for hook_name in ("restore_on_failure", "release_rollback_on_failure"):
            hook_result = self.run_hook(hook_name)
            if not hook_result["ok"]:
                self.errors.append(hook_result["error"])
        return result

    def attempt_rollback(self):
        try:
            return self.rollback()
        except Exception as error:
            self.logger.fail("Rollback failed unexpectedly.")
            return {
                "ok": False,
                "error": "Rollback failed unexpectedly: {0}.".format(error),
                "diagnostics": [],
            }

    def _run_stages(self):
        preflight_result = self.preflight()
        if not preflight_result["ok"]:
            self.errors.extend(preflight_result["errors"])
            return

        self.deployment_identity = preflight_result.get("deployment_identity")
        self.compose_command = preflight_result["compose_command"]

        if self.config.get("backup_enabled", True):
            hook_result = self.run_hook("backup_before_deploy")
            if not hook_result["ok"]:
                self.errors.append(hook_result["error"])
                return

        if self.config.get("database", {}).get("services"):
            database_result = self.start_database()
            if not database_result["ok"]:
                self.errors.append(database_result["error"])
                return

        if self.config.get("backup_enabled", True):
            self.backup_result = self.backup()
            if not self.backup_result["ok"]:
                self.errors.extend(self.backup_result["errors"])
                return
        else:
            self.logger.warning("Backups are disabled.")
            self.backup_result = {"ok": True, "errors": [], "skipped": True}

        compose_result = self.validate(self.compose_command)
        if not compose_result["ok"]:
            self.errors.append(compose_result["error"])
            return

        hook_result = self.run_hook("release_before_deploy")
        if not hook_result["ok"]:
            self.errors.append(hook_result["error"])
            return

        # A failed deploy may have changed services after this point.
        self.deployment_started = True
        deploy_result = self.deploy(self.compose_command)
        if not deploy_result["ok"]:
            self.errors.append(deploy_result["error"])
            self.rollback_result = self.attempt_recovery()
            return

        health_result = self.health_checks()
        if not health_result["ok"]:
            self.errors.extend(health_result["errors"])
            self.diagnostics.extend(health_result.get("diagnostics", []))
            self.rollback_result = self.attempt_recovery()
            return

        identity_result = self.record_deployment_identity()
        if not identity_result["ok"]:
            self.errors.append(identity_result["error"])
            self.logger.fail(identity_result["error"])
            self.rollback_result = self.attempt_recovery()
            return

        self.status = "successful"

    def run(self):
        self.initialize()

        try:
            try:
                self.lock_result = self.acquire_lock()
                if self.lock_result["ok"]:
                    self._run_stages()
                else:
                    self.errors.append(self.lock_result["error"])
            except Exception as error:
                self.errors.append("An unexpected error occurred: {0}.".format(error))
                self.logger.fail("An unexpected error occurred during deployment.")
                if self.deployment_started:
                    self.rollback_result = self.attempt_recovery()
        finally:
            # Always clean up and report, even when a stage raises an error.
            if self.lock_result and self.lock_result["ok"]:
                try:
                    if self.config.get("cleanup_enabled", True):
                        self.cleanup_result = self.cleanup()
                    else:
                        self.logger.warning("Cleanup is disabled.")
                        self.cleanup_result = {"ok": True, "errors": [], "skipped": True}
                    if not self.cleanup_result["ok"]:
                        self.errors.extend(self.cleanup_result["errors"])
                except Exception as error:
                    self.errors.append("Cleanup failed unexpectedly: {0}.".format(error))
                    self.logger.fail("Cleanup failed unexpectedly.")
            else:
                self.cleanup_result = {"ok": True, "errors": [], "skipped": True}

            if self.lock_result and self.lock_result["ok"]:
                release_result = self.release_lock()
                if not release_result["ok"]:
                    self.errors.append(release_result["error"])

            if self.rollback_result and not self.rollback_result["ok"]:
                self.errors.append(self.rollback_result["error"])
            if self.errors:
                self.status = "failed"

            self.report()
            self.logger.close()
        if self.status == "successful":
            return 0
        return 1


def run(config, command_runner=None):
    runner = DeploymentRunner(config, command_runner)
    return runner.run()
