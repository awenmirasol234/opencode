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
projects only need the configuration file. The runner calls these steps in
order: preflight, backup, validation, deployment, health checks, cleanup, and
reporting. A project with a special stage can override one of the small stage
methods.

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

## Failure behavior

- Preflight, backup, and Compose validation failures stop without rollback.
- Deployment and health-check failures trigger the configured rollback.
- Unexpected failures trigger rollback after deployment may have started.
- Cleanup and final reporting run after every outcome.
- Backups, logs, volumes, and persistent data are not removed by cleanup.
- Exit code `0` is returned only after deployment and health checks succeed.

After deployment, the toolkit waits 30 seconds for containers to start and then
runs each configured health check once. It does not poll health checks.

## Tests

The tests use fake command runners and do not change Docker services:

```text
python -m unittest discover -s tests -v
```
