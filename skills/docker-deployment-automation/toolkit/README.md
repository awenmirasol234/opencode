# Docker Deployment Toolkit

This is a small Python toolkit for safe Docker Compose deployments.

It uses only the Python standard library at runtime. Each project provides a
plain Python configuration dictionary. The toolkit does not guess database,
health-check, migration, or rollback commands.

## Install

From this directory, install it in the project environment:

```text
python -m pip install -e .
```

The package can also be used directly without installation by running from
this directory.

## Use

Copy `examples/deploy_config.py` to the project as `deploy_config.py`, then
replace the example health and rollback commands with project commands.

Run either command:

```text
python -m docker_deployment --config deploy_config.py
docker-deploy --config deploy_config.py
```

Commands are passed as argument lists. They are not run through a shell.

The fixed deployment order is implemented by `DeploymentRunner.run()`. Most
projects only need configuration. A project with a special stage can subclass
`DeploymentRunner` and override one plain stage method.

## Configuration

Required useful values are:

- `project_dir`: project root.
- `compose_files`: Compose files to use.
- `env_file`: optional environment file.
- `required_env`: required variable names.
- `deployment`: commit SHA and rollback state configuration.
- `backup_paths`: project files or directories to preserve.
- `health_checks`: explicit command or URL checks.
- `rollback.command`: explicit project recovery command.

Optional values include `database`, `required_services`,
`minimum_free_space_mb`, `temporary_paths`, `backup_dir`, and `log_dir`.

Database configuration supports an explicit readiness command followed by an
explicit backup command. The backup command may use these placeholders:

- `{backup_dir}`
- `{backup_file}`
- `{project_dir}`

Rollback commands may use `{backup_dir}` and `{project_dir}`.
Deployment and rollback commands may also use `{commit_sha}` and
`{previous_commit_sha}`. The commit SHA must be a full 40-character Git SHA.

The deployment configuration uses the commit SHA as the single release
identity:

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

## Failure behavior

- Preflight, backup, and Compose validation failures stop without rollback.
- Deployment and health-check failures trigger the configured rollback.
- Unexpected failures trigger rollback after deployment may have started.
- Cleanup and final reporting run after every outcome.
- Backups, logs, volumes, and persistent data are not removed by cleanup.
- Exit code `0` is returned only after deployment and health checks succeed.

## Tests

The tests use fake command runners and do not change Docker services:

```text
python -m unittest discover -s tests -v
```
