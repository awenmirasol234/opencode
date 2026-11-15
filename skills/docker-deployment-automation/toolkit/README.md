# Docker Deployment Toolkit

This is a small Python toolkit for safe Docker Compose deployments.

Each project provides one configuration file. The file can be a plain Python
dictionary or a YAML file. The toolkit does not guess database, health-check,
migration, or rollback commands.

The code uses beginner-friendly Python: simple functions, clear `if` statements,
lists, and dictionaries. Each deployment step is kept in its own small file.

## Install in another project

Keep a local copy of this `toolkit` folder. From the target project's folder,
install the toolkit with the path to that folder:

```text
python -m pip install ./path/to/toolkit
```

On Windows, a local path can also look like this:

```text
python -m pip install .\tools\docker-deployment-toolkit
```

Use editable installation when developing the toolkit. Changes to the local
toolkit files will then be used immediately:

```text
python -m pip install -e ./path/to/toolkit
```

Python files need only the standard library. YAML configuration files need
PyYAML, which the installer adds automatically.

## Use

Copy `examples/deploy_config.py` or `examples/deploy_config.yaml` from the
local toolkit folder to the target project. Replace the example health and
rollback commands with commands for that project.

Run the command from the target project folder:

```text
docker-deploy --config deploy_config.py
```

You can also run the module directly:

```text
python -m docker_deployment --config deploy_config.yaml
```

Commands are written as lists. For example:

```python
["docker", "compose", "up", "-d"]
```

The commands are not run through a shell.

The fixed deployment order is implemented by `DeploymentRunner.run()`. Most
projects only need the configuration file. The runner:

1. Reads the environment, builds the deployment identity, and takes the lock.
2. Runs the preflight checks.
3. Runs the optional backup preparation hook.
4. Starts configured database services, waits for readiness, and creates the backup.
5. Validates the Compose configuration.
6. Runs the optional release hook.
7. Pulls images and deploys the application.
8. Polls health checks until they pass or time out.
9. Saves the deployment SHA only after successful health checks.
10. Rolls back a failed deployment and runs the recovery hooks.
11. Removes only safe temporary paths and releases the lock.
12. Reports the result.

A project with a special stage can override one of the small stage methods.

## Configuration

Required useful values are:

- `project_dir`: project root.
- `compose_files`: Compose files to use.
- `env_file`: optional environment file.
- `required_env`: required variable names.
- `deployment`: commit SHA and rollback state configuration.
- `lock_file`: deployment lock path, which prevents concurrent deployments.
- `backup_paths`: project files or directories to preserve.
- `health_checks`: explicit command, URL, or container checks.
- `rollback.command`: explicit project recovery command.
- `required_images`: Docker images that must be available during preflight.

Optional values include `database`, `compose`, `required_services`,
`temporary_paths`, `protected_paths`, `backup_dir`, and `log_dir`.

The optional `backup_enabled`, `rollback_enabled`, `deployment_lock`, and
`cleanup_enabled` settings default to `True`.

When `deployment_lock` is disabled, the runner does not create or remove a
lock file. When cleanup is disabled, configured temporary paths are preserved.
Disabling backups or rollback is reported in the final result.

The lock defaults to `.deployment/deployment.lock`. It is created atomically
and must stay inside the project. The runner does not remove a lock file that
it did not create; verify that no deployment is active before removing a stale
lock manually.

### YAML configuration

A YAML file uses the same values in named sections. Copy
`examples/deploy_config.yaml` and edit it:

```yaml
project_dir: "."
compose_files:
  - compose.yaml
env_file: .env
required_env:
  - APP_ENV
deployment:
  commit_sha_env: GIT_COMMIT_SHA
  state_file: .deployment/current-sha
  require_previous_sha: false
locks:
  enabled: true
  file: .deployment/deployment.lock
backup:
  enabled: true
  dir: backups
  paths:
    - compose.yaml
directories:
  log_dir: logs
  temp_paths:
    - .deployment-tmp
  protected_paths:
    - data
services:
  database:
    services: []
    readiness_command: []
    readiness_timeout: 120
    readiness_interval: 5
    readiness_retries: 30
    backup_command: []
    backup_file: database.backup
health:
  timeout: 120
  interval: 5
  checks: []
compose:
  pull_args:
    - pull
  deploy_args:
    - up
    - -d
  rollback_args:
    - up
    - -d
rollback:
  command:
    - python
    - scripts/rollback.py
    - "{backup_dir}"
hooks: {}
cleanup:
  enabled: true
```

### Preflight checks

Before changing services, the runner checks the project directory, Compose
files, environment file, required environment values, read and write
permissions, the deployment SHA, Docker Compose, and the Docker Engine. Each
value in `required_images` is checked with `docker image inspect`. A failed
required check stops the deployment before backup or rollback.

Database configuration supports optional database services, an explicit
readiness command, and an explicit backup command. Configured services are
started with Compose before readiness polling begins. Set `readiness_timeout`
for a time-based limit. The default timeout is 120 seconds and the default
polling interval is 5 seconds. Use `readiness_retries` instead of a timeout
when a fixed retry count is preferred. The backup command may use these
placeholders:

- `{backup_dir}`
- `{backup_file}`
- `{project_dir}`

Configured database services start before readiness checks. The database
backup file must exist and must not be empty after the backup command runs.

Configuration and database backups use unique timestamped directories. Copied
files are compared with their sources before the deployment continues.

Rollback commands may use `{backup_dir}` and `{project_dir}`.
Deployment and rollback commands may also use `{commit_sha}` and
`{previous_commit_sha}`. The commit SHA must be a full 40-character Git SHA.

The deployment configuration uses one commit SHA to identify the release:

```python
"deployment": {
    "commit_sha_env": "GIT_COMMIT_SHA",
    "state_file": ".deployment/current-sha",
    "require_previous_sha": False,
},
```

The runner reads the new SHA from the configured environment variable or
environment file, validates it before backups, and records it only after
deployment and health checks succeed. Set `require_previous_sha` to `True`
when rollback must have an existing deployed version.

Optional `hooks` values run project commands at fixed points in the
deployment. Hook names are `backup_before_deploy`, `release_before_deploy`,
`restore_on_failure`, and `release_rollback_on_failure`. Each hook value is
a command list and may use the `{project_dir}`, `{backup_dir}`,
`{commit_sha}`, and `{previous_commit_sha}` placeholders. A failed hook stops
the deployment. A failed failure hook is reported as a recovery error.

Required health checks are polled until they pass or the configured timeout
expires:

```python
"health": {
    "timeout": 120,
    "interval": 5,
},
```

Health checks support `command`, `url`, and `container` types. Container checks
inspect Docker state and health status. `starting` and `unhealthy` states are
polled; exited and dead containers fail immediately. Set `required` to `False`
for a noncritical check. Container checks require a Compose healthcheck.

The deployment pulls images before starting application services. The default is
`compose.pull_args: ["pull"]`. Set `compose.pull_args` to an empty list to skip
that step. Failed health checks include command output and container status.

Cleanup never removes backups, logs, deployment state, or Docker volumes. Add
host-mounted database or application data paths to `protected_paths` so they
cannot be listed as temporary cleanup paths.

## Failure behavior

- Preflight, backup, and Compose validation failures stop without rollback.
- A lock failure stops before preflight and skips cleanup commands.
- Deployment and health-check failures trigger the configured rollback.
- Cleanup and final reporting run after every outcome.
- Backups, logs, volumes, and persistent data are not removed by cleanup.
- Exit code `0` is returned only after deployment and health checks succeed.

A deployment lock is held from the start of the deployment through cleanup and
is released on every completed run that created it.

## Tests

The tests use fake command runners and do not change Docker services:

```text
python -m unittest discover -s tests -v
```
