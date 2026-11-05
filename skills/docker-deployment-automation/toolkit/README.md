# Docker Deployment Toolkit

This is a small Python toolkit for safe Docker Compose deployments.

It uses only the Python standard library at runtime. Each project provides a
plain Python configuration dictionary. The toolkit does not guess database,
health-check, migration, or rollback commands.

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

The toolkit has no runtime dependencies outside the Python standard library.

## Use

Copy `examples/deploy_config.py` from the local toolkit folder to the target
project as `deploy_config.py`. Replace the example health and rollback commands
with commands for that project.

Run the command from the target project folder:

```text
docker-deploy --config deploy_config.py
```

You can also run the module directly:

```text
python -m docker_deployment --config deploy_config.py
```

Commands are written as lists. For example:

```python
["docker", "compose", "up", "-d"]
```

The commands are not run through a shell.

The fixed deployment order is implemented by `DeploymentRunner.run()`. Most
projects only need the configuration file. The runner acquires the deployment
lock, runs preflight, runs the optional backup hook, waits for database
readiness, creates backups, validates Compose, runs the optional release hook,
deploys, polls health checks, saves the SHA, cleans up, and reports the result.
A deployment or health-check failure triggers the configured rollback before
cleanup. A project with a special stage can override one of the small stage
methods.

## Configuration

Required useful values are:

- `project_dir`: project root.
- `compose_files`: Compose files to use.
- `env_file`: optional environment file.
- `required_env`: required variable names.
- `deployment`: commit SHA and rollback state configuration.
- `lock_file`: deployment lock path, which prevents concurrent deployments.
- `backup_paths`: project files or directories to preserve.
- `health_checks`: explicit command or URL checks.
- `rollback.command`: explicit project recovery command.
- `required_images`: Docker images that must be available during preflight.

Optional values include `database`, `required_services`, `minimum_free_space_mb`,
`temporary_paths`, `protected_paths`, `backup_dir`, and `log_dir`.

The optional `backup_enabled`, `rollback_enabled`, `deployment_lock`, and
`cleanup_enabled` settings default to `True`.

The lock defaults to `.deployment/deployment.lock`. It is created atomically
and must stay inside the project. The runner does not remove an existing lock;
verify that no deployment is active before removing a stale lock manually.

Database configuration supports optional database services, an explicit
readiness command, and an explicit backup command. Set `readiness_timeout` for
a time-based limit; otherwise `readiness_retries` and `readiness_interval`
control the wait. The
backup command may use these placeholders:

- `{backup_dir}`
- `{backup_file}`
- `{project_dir}`

Configured database services start before readiness checks. Database backup
files are checked for existence and non-empty content. A project-specific
`verify_command` can perform a stronger integrity check.

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

Health checks are polled until all checks pass or the configured timeout
expires:

```python
"health": {
    "timeout": 120,
    "interval": 5,
},
```

Health checks support `command`, `url`, and `container` types. Container checks
inspect Docker state and health status. `starting` and `unhealthy` states are
polled; missing, exited, and dead containers fail immediately. Set `required`
to `False` for a noncritical check. Container checks require a Compose
healthcheck unless `require_health` is set to `False`.

The deployment pulls images before starting application services. Set
`compose.pull_args` to an empty list to skip that step. Failed container health
checks include recent container logs and health output when available.

Cleanup never removes backups, logs, deployment state, or Docker volumes. Add
host-mounted database or application data paths to `protected_paths` so they
cannot be listed as temporary cleanup paths.

## Failure behavior

- Preflight, backup, and Compose validation failures stop without rollback.
- A lock failure stops before preflight and skips cleanup commands.
- Deployment and health-check failures trigger the configured rollback.
- Unexpected failures trigger rollback after deployment may have started.
- Cleanup and final reporting run after every outcome.
- Backups, logs, volumes, and persistent data are not removed by cleanup.
- Exit code `0` is returned only after deployment and health checks succeed.

After deployment, the toolkit polls each configured health check until the
application is ready or the health timeout expires. A deployment lock is held
from preflight through cleanup and is released on every completed run.

## Tests

The tests use fake command runners and do not change Docker services:

```text
python -m unittest discover -s tests -v
```
