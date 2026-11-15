# How the Docker Deployment Automation Works

This document explains the deployment toolkit in plain words. You do not need
to know Python or Docker to read it.

If you want the technical details, read `toolkit/README.md` instead.

## What this tool does

The tool starts your Docker Compose application in the right order. It checks
that everything is ready before it changes anything. It takes a backup first.
It watches the application after it starts. If something goes wrong, it puts
the old version back.

You give the tool one file that describes your project. The tool never guesses
what your commands should be.

## The flow in one picture

```text
  1. Take the lock
         |
  2. Run the checks .............. fail --> stop
         |
  3. Make a backup .............. fail --> stop
         |
  4. Check the Compose file ..... fail --> stop
         |
  5. Start the app .............. fail --> undo, then stop
         |
  6. Watch the health checks .... fail --> undo, then stop
         |
  7. Remember the version
         |
  8. Tidy up
         |
  9. Report the result
```

Two paths lead away from the main line:

- **stop** means the run ends. Nothing was changed, so there is nothing to undo.
- **undo** means the tool runs your rollback command to bring the old version
  back, and then the run ends.

## What happens at each step

### 1. Take the lock

The tool creates a small file, called the lock file, in your project. If the
file is already there, another deployment is already running, so this run stops
right away.

The lock file must live inside your project. The tool refuses to use a path
that points outside it.

The tool never removes a lock file that it did not create. If a run is killed
and the lock is left behind, check that no deployment is running before you
delete it by hand.

### 2. Run the checks

Before the tool touches anything, it checks that the project is ready:

- the project folder is there
- the Compose file is there
- the environment file is there
- the environment values you marked as required are present
- the project folder can be read and written
- the commit SHA is a full 40 character Git SHA
- Docker and Docker Compose are installed and running
- every image you listed is already on the machine

If any check fails, the run stops here. Nothing has changed yet, so there is
no need to undo anything.

### 3. Make a backup

The tool copies the files you listed into a new folder with the current time
in its name. It then compares each copy with the original. If a copy does not
match, the run stops.

If your project has a database, the tool can start the database first, wait
until it answers, and then save a dump of it. The dump must exist and must not
be empty, or the run stops.

### 4. Check the Compose file

The tool asks Docker Compose to read the configuration and print it. If the
file has a mistake, this fails and the run stops. Your running services have
not been touched yet.

### 5. Start the app

The tool pulls the images it needs, then tells Docker Compose to start the
containers.

### 6. Watch the health checks

After the app starts, the tool asks your health checks over and over until
they all pass. It waits a few seconds between tries and gives up after the
timeout you set.

A health check can be one of three things:

- a **command** that must succeed, such as a script that calls your API
- a **URL** that must answer with the status code you expect
- a **container** that must be running and report itself as healthy

If a required health check never passes, the tool treats it like a failed
deployment and undoes it.

### 7. Remember the version

When everything worked, the tool writes the commit SHA to a small file in your
project. The next deployment reads that file, so it knows which version to go
back to if this one fails.

### 8. Tidy up

The tool removes only the temporary paths you listed. It never removes
backups, logs, the deployment state, Docker volumes, or your data. Any path
you list as protected is kept even if it is also listed as temporary.

### 9. Report the result

The tool prints one final line. `0` means everything worked. `1` means
something failed. `2` means the configuration file could not be read at all.

## The configuration file

Your project keeps one Python file, usually called `deploy_config.py`. It
holds one dictionary called `CONFIG`.

These are the values you normally set:

| Value | What it means |
|---|---|
| `project_dir` | the folder your project lives in |
| `compose_files` | the Compose file to use, such as `compose.yaml` |
| `env_file` | the file with your environment values, usually `.env` |
| `required_env` | the names of environment values that must be present |
| `deployment` | where to read the commit SHA and where to remember it |
| `health_checks` | the checks that prove your app is working |
| `rollback.command` | the command that puts the old version back |

These are the values you set only when you need them:

| Value | What it means |
|---|---|
| `required_images` | images that must already be on the machine |
| `required_services` | Compose services that must exist in the Compose file |
| `database` | how to start, wait for and save your database |
| `compose` | the arguments used to pull, start and roll back |
| `hooks` | your own commands that run at fixed points |
| `backup_paths` | the files to copy before deploying |
| `temporary_paths` | the paths to delete afterwards |
| `protected_paths` | the paths that must never be deleted |
| `backup_enabled` | set to `False` to skip the backup |
| `rollback_enabled` | set to `False` to skip the undo |
| `cleanup_enabled` | set to `False` to skip the tidy up |
| `deployment_lock` | set to `False` to skip the lock |

Every value has a sensible default, so you only fill in what your project
needs. The full list of defaults lives in `toolkit/docker_deployment/config.py`.

## Reading the output

While a step is running, the tool shows a small spinning dot and the message
for that step:

```text
⠋ Starting the application.
```

When a step finishes, the tool shows the result with a level instead:

```text
[OK] The application container is healthy.
[FAIL] The Docker Engine is not available.
[WARN] The protected path was preserved: data.
```

- `[OK]` means it worked.
- `[WARN]` means something worth knowing happened, but the run continues.
- `[FAIL]` means it did not work.

A line never shows a level and the spinning dot at the same time.

The log file keeps only the finished lines, with the time on each one:

```text
2026-11-15T17:56:24 [OK] The project directory was found.
2026-11-15T17:56:26 [FAIL] The Docker Engine is not available.
```

Log files live in the `logs` folder, one file per run. They are never deleted
by the cleanup step.

## When something goes wrong

| What broke | What the tool does | Result |
|---|---|---|
| The lock file already exists | stops before anything else | exit code `1` |
| A check failed | stops, nothing was changed | exit code `1` |
| The backup failed | stops, nothing was changed | exit code `1` |
| The Compose file is not valid | stops, nothing was changed | exit code `1` |
| The app did not start | runs your rollback command, then stops | exit code `1` |
| A health check never passed | runs your rollback command, then stops | exit code `1` |
| The rollback command failed | reports the failure | exit code `1` |
| The configuration file cannot be read | stops before starting | exit code `2` |

The tool always tries to tidy up and report the result, whatever happened.

## What it will never do

- It will never guess your commands. It runs only what your configuration file
  names.
- It will never run a command through a shell. Every command is a list of
  arguments, so nothing is interpreted as shell syntax.
- It will never delete your data. Backups, logs, volumes, the deployment state
  and protected paths are always kept.
- It will never print a secret. Passwords, tokens and private keys are replaced
  with `[REDACTED]` in the terminal and in the log file.
- It will never remove a lock file it did not create.

## A worked example

A small project with one web container:

```python
CONFIG = {
    "project_dir": ".",
    "compose_files": ["compose.yaml"],
    "env_file": ".env",
    "required_env": ["APP_ENV"],
    "deployment": {
        "commit_sha_env": "GIT_COMMIT_SHA",
        "state_file": ".deployment/current-sha",
    },
    "health": {
        "timeout": 60,
        "interval": 2,
    },
    "health_checks": [
        {
            "name": "Application container",
            "type": "container",
            "service": "app",
        }
    ],
    "rollback": {
        "command": ["docker", "compose", "down"],
    },
}
```

The `.env` file holds the values, and the commit SHA must be a full 40
character Git SHA:

```text
APP_ENV=production
GIT_COMMIT_SHA=0123456789abcdef0123456789abcdef01234567
```

The run looks like this:

```text
⠋ Running the preflight checks.
[OK] The project directory was found.
[OK] The Compose files were found.
[OK] The environment file was found.
[OK] The required environment values are available.
[OK] The project directory is readable and writable.
[OK] The deployment commit SHA is valid.
[OK] Docker Compose is available.
[OK] The Docker Engine is available.
[OK] The required Docker images are available.
[OK] The preflight checks completed successfully.
⠋ Creating the backup.
[OK] The backup was created at C:\projects\myapp\backups\backup_20261115_180102.
⠋ Validating the Docker Compose configuration.
[OK] The Docker Compose configuration is valid.
⠋ Deploying the application.
[OK] The application images were pulled.
[OK] The application deployment completed successfully.
⠋ Waiting for the health checks.
[OK] Application container passed.
[OK] The safe cleanup completed successfully.
[OK] The deployment finished successfully.
```

Afterwards the project folder holds:

| Path | What it is |
|---|---|
| `logs/deployment_20261115_180102.log` | the finished lines of this run |
| `.deployment/current-sha` | the commit SHA that is now live |
| `backups/backup_20261115_180102/` | the copy of your files |

The tool prints the full path of the backup folder, as in the example above.
