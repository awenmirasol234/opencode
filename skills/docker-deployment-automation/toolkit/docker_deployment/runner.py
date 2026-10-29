from datetime import datetime

from .backup import create_backups
from .cleanup import clean
from .commands import run_command
from .config import environment_values, project_path, save_deployment_identity
from .deployment import deploy as deploy_application
from .deployment import validate_compose
from .health import run_health_checks
from .logger import Logger
from .preflight import run_preflight
from .rollback import rollback as restore_rollback


def _log_path(config):
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

    def initialize(self):
        secret_values = list(environment_values(self.config).values())
        self.logger = Logger(_log_path(self.config), secret_values=secret_values)
        self.logger.info("Starting the Docker deployment.")

    def preflight(self):
        return run_preflight(self.config, self.command_runner, self.logger)

    def backup(self):
        return create_backups(self.config, self.command_runner, self.logger)

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
        return run_health_checks(self.config, self.command_runner, self.logger)

    def rollback(self):
        return restore_rollback(
            self.config,
            self.backup_result or {},
            self.command_runner,
            self.logger,
            self.deployment_identity,
        )

    def record_deployment_identity(self):
        return save_deployment_identity(self.deployment_identity)

    def cleanup(self):
        return clean(self.config, self.logger)

    def report(self):
        self.logger.info("Deployment result: {0}.".format(self.status))
        if self.backup_result and self.backup_result.get("backup_dir"):
            self.logger.info("Backup location: {0}.".format(self.backup_result["backup_dir"]))
        if self.rollback_result:
            rollback_status = "failed"
            if self.rollback_result["ok"]:
                rollback_status = "successful"
            self.logger.info("Rollback result: {0}.".format(rollback_status))
        if self.cleanup_result:
            cleanup_status = "failed"
            if self.cleanup_result["ok"]:
                cleanup_status = "successful"
            self.logger.info("Cleanup result: {0}.".format(cleanup_status))
        for error in self.errors:
            self.logger.fail(error)

    def attempt_rollback(self):
        try:
            return self.rollback()
        except Exception as error:
            self.logger.fail("Rollback failed unexpectedly.")
            return {
                "ok": False,
                "error": "Rollback failed unexpectedly: {0}.".format(error),
            }

    def run(self):
        self.initialize()

        try:
            preflight_result = self.preflight()
            if not preflight_result["ok"]:
                self.errors.extend(preflight_result["errors"])
            else:
                self.deployment_identity = preflight_result.get("deployment_identity")
                self.backup_result = self.backup()
                if not self.backup_result["ok"]:
                    self.errors.extend(self.backup_result["errors"])
                else:
                    compose_result = self.validate(
                        preflight_result["compose_command"]
                    )
                    if not compose_result["ok"]:
                        self.errors.append(compose_result["error"])
                    else:
                        self.deployment_started = True
                        deploy_result = self.deploy(
                            preflight_result["compose_command"]
                        )
                        if not deploy_result["ok"]:
                            self.errors.append(deploy_result["error"])
                            self.rollback_result = self.attempt_rollback()
                        else:
                            health_result = self.health_checks()
                            if not health_result["ok"]:
                                self.errors.extend(health_result["errors"])
                                self.rollback_result = self.attempt_rollback()
                            else:
                                identity_result = self.record_deployment_identity()
                                if not identity_result["ok"]:
                                    self.errors.append(identity_result["error"])
                                    self.logger.fail(identity_result["error"])
                                    self.rollback_result = self.attempt_rollback()
                                else:
                                    self.status = "successful"
        except Exception as error:
            self.errors.append("An unexpected error occurred: {0}.".format(error))
            self.logger.fail("An unexpected error occurred during deployment.")
            if self.deployment_started:
                self.rollback_result = self.attempt_rollback()

        try:
            self.cleanup_result = self.cleanup()
            if not self.cleanup_result["ok"]:
                self.errors.extend(self.cleanup_result["errors"])
        except Exception as error:
            self.errors.append("Cleanup failed unexpectedly: {0}.".format(error))
            self.logger.fail("Cleanup failed unexpectedly.")

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
