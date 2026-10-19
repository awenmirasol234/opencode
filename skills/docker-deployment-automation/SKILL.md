---
name: docker-deployment-automation
description: Build or improve a safe, modular Python deployment runner for Docker Compose full-stack applications.
---

# Docker Deployment Automation

Apply this skill when you create or improve a Python deployment system for a Docker Compose application.

Launch the deployment with:

```bash
python deploy.py
```

## Before changing

Before you implement anything:

- Inspect the project structure, technologies, Compose files, scripts, environment variables, secrets, databases, services, and health endpoints.
- Reuse existing scripts and configuration where appropriate.
- Preserve existing functionality and avoid unrelated changes.
- If the project is empty, create the required structure.
- Do not invent database, Nginx, API, or health-check commands that the project does not support.
- Treat external configuration and environment values as untrusted input. Fail safely instead of guessing when project behavior is unclear.

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

Give each module one clear responsibility. Keep all orchestration in `deploy.py`.

## Deployment flow

### 1. Initialize the logger

Initialize terminal and file logging. Record timestamps, stages, command results, errors, and final results. Preserve logs between executions.

Never log secret values, passwords, tokens, private keys, or complete environment contents. Redact sensitive command output.

Use this readable terminal format:

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

Keep file logs uncolored and include timestamps in them. Disable terminal colors when output is not a TTY or when the `NO_COLOR` environment variable is set. Keep colors and terminal formatting from affecting exit codes or log content.

### 2. Run preflight checks

Validate required tools, Docker, Docker Compose, Compose configuration, required environment variable names, permissions, disk space, and project-specific prerequisites.

Stop immediately when a required check fails. Do not deploy or roll back. Run safe cleanup, generate the final summary, and return a nonzero exit code.

### 3. Create backups

Back up the database when supported, along with required configuration or recovery files. Use unique timestamped locations. Preserve existing backups. Verify successful completion. Never overwrite the only valid backup.

Stop immediately when a required backup fails. Do not deploy or roll back. Preserve all recovery files, run safe cleanup, generate the final summary, and return a nonzero exit code.

### 4. Validate Compose

Validate the Docker Compose configuration before changing running services. Keep this validation in `scripts/deployment.py`. Stop when validation fails.

### 5. Deploy the application

Deploy with the project’s Docker Compose configuration. Capture command output and exit codes. Record failures. Avoid destructive Docker commands. Treat deployment failures as rollback-triggering failures.

### 6. Run health checks

Verify applicable container status, Nginx availability, backend API availability, and representative application functionality. Skip checks for services the project does not use. Use configurable timeouts, retry limits, polling intervals, endpoints, and expected responses.

Trigger rollback when required health checks fail.

### 7. Roll back when required

Restore the previous working application version after a deployment or health-check failure. Use preserved recovery artifacts.

- Restore database backups only when explicitly required and safely supported.
- Verify application health after rollback.
- Preserve backups, rollback files, logs, and diagnostics.
- Do not claim rollback succeeded without successful recovery and verification.
- Report rollback failures and return a nonzero exit code.

### 8. Clean up safely

Remove only eligible temporary files and resources. Never remove Docker volumes, persistent application or database data, backups, recovery files, deployment logs, or resources required for rollback.

Never use destructive Docker cleanup commands that can remove persistent data. Attempt cleanup after successful and failed executions.

### 9. Report the result

Generate a summary for every outcome. Include:

- Final deployment status
- Completed and failed stages
- Health-check results
- Rollback outcome
- Cleanup outcome
- Relevant errors
- Backup and log locations

Run final reporting after preflight failures, backup failures, validation failures, deployment failures, health-check failures, rollback failures, and unexpected exceptions.

### 10. Exit

Return exit code `0` only when deployment and required health checks succeed. Return a nonzero exit code for every required failure, failed rollback, or unexpected exception.

## Orchestration and failure handling

Use `deploy.py` as the only orchestration entry point:

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

- Stop normal deployment after a required stage fails.
- Skip rollback when preflight or backup fails because no deployment changes were made.
- Do not roll back Compose validation failures because validation occurs before deployment changes.
- Attempt rollback after deployment or health-check failures.
- When an unexpected exception occurs after deployment changes may have started, attempt rollback using the same recovery rules.
- Handle command failures and unexpected exceptions explicitly.
- Use consistent result objects or well-defined exceptions between modules.
- Preserve the original failure when reporting secondary rollback or cleanup failures.
- Run cleanup and final reporting from a protected finalization path, including after unexpected exceptions.

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

## Expected deliverable

Provide a concise summary. Include:

1. List created or modified files.
2. Describe implementation and failure-handling behavior.
3. List verification commands that you ran.
4. Report verification results.
5. Document project-specific assumptions, unsupported checks, or required configuration.

## Verification checklist

Use mocks or safe test doubles for commands that could affect production services. Verify the following:

- [ ] Verify the execution order.
- [ ] Confirm that preflight and backup failures stop deployment and do not trigger rollback.
- [ ] Confirm that Compose validation occurs before deployment.
- [ ] Confirm that Compose validation failures do not trigger rollback.
- [ ] Confirm that deployment and health-check failures trigger rollback.
- [ ] Confirm that rollback failures are reported and return a nonzero exit code.
- [ ] Confirm that final reporting runs for every outcome.
- [ ] Confirm that cleanup protects backups, logs, volumes, persistent data, and recovery files.
- [ ] Confirm that secrets are absent from terminal and log output.
- [ ] Confirm that existing tests continue to pass.

Run relevant project checks and tests. Report unavailable checks instead of claiming that they passed.
