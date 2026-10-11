---
name: docker-deployment-automation
description: Build or improve a safe, modular Python deployment runner for Docker Compose full-stack applications.
---

# Docker Deployment Automation

Use this skill when creating or improving a Python deployment system for a Docker Compose application.

The deployment must be launched with:

```bash
python deploy.py
```

## Before changing

Before implementing anything:

- Inspect the project structure, technologies, Compose files, scripts, environment variables, secrets, databases, services, and health endpoints.
- Reuse existing scripts and configuration where appropriate.
- Preserve existing functionality and avoid unrelated changes.
- If the project is empty, create the required structure.
- Do not invent database, Nginx, API, or health-check commands unsupported by the project.
- Treat external configuration and environment values as untrusted input. Prefer safe failure over guessing when project behavior is unclear.

## Required structure

```text
deploy.py
scripts/
    logger.py
    preflight.py
    backup.py
    deployment.py
    health.py
    rollback.py
    cleanup.py
```

Each module must have one clear responsibility. Keep all orchestration in `deploy.py`.

## Deployment flow

### 1. Initialize the logger

Initialize terminal and file logging. Record timestamps, stages, command results, errors, and final results. Preserve logs between executions.

Never log secret values, passwords, tokens, private keys, or complete environment contents. Redact sensitive command output.

Terminal output must use this readable format:

```text
[INFO] Starting Docker deployment...

[INFO] Step 1: Preflight check...
[ OK ] Docker is running.
[ OK ] Docker Compose is available.
[ OK ] .env file found.
[PASS] Preflight check passed.

[INFO] Step 2: Backup...
[ OK ] Database backup saved.
[ OK ] Configuration files backed up.
[PASS] Backup complete: backups/backup_20261011_092119

[INFO] Step 3: Deploy...
[INFO] Pulling db image...
```

Use these message levels consistently:

- `[INFO]` for stages and progress messages.
- `[ OK ]` for an individual successful check or action.
- `[PASS]` for a completed stage.
- `[WARN]` for a non-fatal warning.
- `[FAIL]` for a failed check, action, or stage.

Use ANSI colors only for interactive terminal output:

- `[INFO]` and stage headings: cyan or blue.
- `[ OK ]` and `[PASS]`: green.
- `[WARN]`: yellow.
- `[FAIL]`: red.

Keep file logs uncolored and include timestamps in them. Disable terminal colors when output is not a TTY or when the `NO_COLOR` environment variable is set. Do not make colors or terminal formatting affect exit codes or log content.

### 2. Run preflight checks

Validate required tools, Docker, Docker Compose, Compose configuration, required environment variable names, permissions, disk space, and project-specific prerequisites.

If a required check fails, stop immediately. Do not deploy or roll back. Run safe cleanup, generate the final summary, and return a nonzero exit code.

### 3. Create backups

Back up the database when supported, along with required configuration or recovery files. Use unique timestamped locations, preserve existing backups, verify successful completion, and never overwrite the only valid backup.

If a required backup fails, stop immediately. Do not deploy or roll back. Preserve all recovery files, run safe cleanup, generate the final summary, and return a nonzero exit code.

### 4. Validate Compose

Validate the Docker Compose configuration before changing running services. Keep this validation in `scripts/deployment.py`. Stop if validation fails.

### 5. Deploy the application

Deploy with the project’s Docker Compose configuration. Capture command output and exit codes, record failures, avoid destructive Docker commands, and treat deployment failures as rollback-triggering failures.

### 6. Run health checks

Verify applicable container status, Nginx availability, backend API availability, and representative application functionality. Skip checks for services the project does not use. Use configurable timeouts, retry limits, polling intervals, endpoints, and expected responses.

Trigger rollback when required health checks fail.

### 7. Roll back when required

Restore the previous working application version after deployment or health-check failure using preserved recovery artifacts.

- Restore database backups only when explicitly required and safely supported.
- Verify application health after rollback.
- Preserve backups, rollback files, logs, and diagnostics.
- Do not claim rollback succeeded without successful recovery and verification.
- Report rollback failures and return a nonzero exit code.

### 8. Clean up safely

Remove only eligible temporary files and resources. Never remove Docker volumes, persistent application or database data, backups, recovery files, deployment logs, or resources required for rollback.

Never use destructive Docker cleanup commands that can remove persistent data. Attempt cleanup after both successful and failed executions.

### 9. Report the result

Generate a summary for every outcome, including:

- Final deployment status
- Completed and failed stages
- Health-check results
- Rollback outcome
- Cleanup outcome
- Relevant errors
- Backup and log locations

Final reporting must run after preflight failures, backup failures, validation failures, deployment failures, health-check failures, rollback failures, and unexpected exceptions.

### 10. Exit

Return exit code `0` only when deployment and required health checks succeed. Return a nonzero exit code for any required failure, failed rollback, or unexpected exception.

## Orchestration and failure handling

`deploy.py` must be the only orchestration entry point:

```text
initialize logger
  -> preflight
  -> backup
  -> validate Compose
  -> deploy
  -> health checks
  -> cleanup
  -> final summary
  -> exit
```

Failure behavior:

- Do not continue normal deployment after a required stage fails.
- Skip rollback when preflight or backup fails because no deployment changes were made.
- Do not roll back Compose validation failures because validation occurs before deployment changes.
- Attempt rollback after deployment or health-check failures.
- If an unexpected exception occurs after deployment changes may have started, attempt rollback using the same recovery rules.
- Handle command failures and unexpected exceptions explicitly.
- Use consistent result objects or well-defined exceptions between modules.
- Preserve the original failure when reporting secondary rollback or cleanup failures.
- Ensure cleanup and final reporting are attempted from a protected finalization path, including after unexpected exceptions.

## Module responsibilities

- `scripts/logger.py`: Configure terminal/file logging and secret redaction.
- `scripts/preflight.py`: Validate tools, configuration, environment, permissions, and disk space.
- `scripts/backup.py`: Create, verify, and describe recovery backups.
- `scripts/deployment.py`: Validate Compose and execute deployment commands.
- `scripts/health.py`: Perform configurable readiness and functionality checks.
- `scripts/rollback.py`: Restore the previous version and verify recovery.
- `scripts/cleanup.py`: Remove only safe temporary resources.
- `deploy.py`: Orchestrate stages, failures, rollback, cleanup, reporting, and exit codes.

## Code quality

- Use standard Python features and existing project dependencies where possible.
- Avoid unnecessary dependencies, abstractions, classes, and configuration files.
- Keep functions focused and names descriptive.
- Follow existing project conventions.
- Keep environment-specific configuration outside source code.
- Add comments only to explain important reasoning or safety behavior.
- Do not suppress errors, weaken tests, or remove assertions to obtain a passing result.

## Verification

Use mocks or safe test doubles for commands that could affect production services. Verify:

- Execution order is correct.
- Preflight and backup failures stop deployment and do not trigger rollback.
- Compose validation occurs before deployment.
- Compose validation failures do not trigger rollback.
- Deployment and health-check failures trigger rollback.
- Rollback failures are reported and return nonzero.
- Final reporting runs for every outcome.
- Cleanup protects backups, logs, volumes, persistent data, and recovery files.
- Secrets are absent from terminal and log output.
- Existing tests continue to pass.

Run relevant project checks and tests. Report unavailable checks rather than claiming they passed.

## Expected deliverable

Provide a concise summary of:

1. Files created or modified.
2. Implementation and failure-handling behavior.
3. Verification commands run.
4. Verification results.
5. Project-specific assumptions, unsupported checks, or required configuration.
