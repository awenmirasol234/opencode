---
name: docker-deployment-automation
description: Build a small, safe Python deployment runner for Docker Compose applications.
---

# Docker Deployment Automation

Build the smallest deployment runner that fits the project. Do not add dependencies,
frameworks, abstractions, or configuration systems unless the project already needs them.

## Before changing code

- Inspect the project, Compose files, environment configuration, services, database, scripts,
  and existing health checks.
- Reuse existing commands and configuration. Do not invent database, Nginx, API, or health
  checks.
- Treat environment values and command output as untrusted. Never log secrets.
- Change only the files needed for this deployment flow.

## Implementation rules

- Use Python and the standard library.
- Use `pathlib` for paths.
- Run commands with `subprocess` argument lists and `shell=False`.
- Keep orchestration in `deploy.py`.
- Create supporting modules only when needed. Possible responsibilities are logging,
  preflight, backup, Compose operations, health checks, rollback, and cleanup. Do not create
  empty or speculative modules.
- Run it with `python deploy.py` from PowerShell or a Unix shell.

## Deployment flow

Run these stages in order:

1. Initialize terminal and file logging.
2. Run preflight checks.
3. Wait for database readiness, when a database is used, and create verified backups.
4. Validate the Compose configuration.
5. Deploy the application.
6. Run the project’s required health checks.
7. Clean up safe temporary resources and report the result.

On a preflight, backup, or Compose validation failure, stop without deploying or rolling back.
On a deployment or health-check failure, roll back using preserved recovery data and verify
health again. Treat an unexpected error as rollback-worthy only if deployment may have started.
Always run cleanup and final reporting, including after exceptions. Return zero only when
deployment and required health checks succeed.

## Logging

- Preserve logs between runs and include timestamps, stages, command results, errors, and the
  final result.
- Redact passwords, tokens, private keys, and other sensitive values from terminal and file
  output. Do not log the complete environment.
- Use clear messages such as `[INFO]`, `[ OK ]`, `[PASS]`, `[WARN]`, and `[FAIL]`.
- Use colors only for interactive terminal output. Disable them for non-TTY output or when
  `NO_COLOR` is set. File logs must remain plain text.

## Required behavior

### Preflight

Check only project requirements: Docker, an available Compose command, Compose files,
required environment names, permissions, disk space, and other documented prerequisites.
Detect the Compose command without relying on shell syntax. Stop at the first required failure.

### Backups

If the project uses a database, wait for its existing readiness condition before backing it up.
Back up required configuration and recovery files as well. Use a unique timestamped directory,
verify each backup, and preserve older valid backups. Do not restore a database backup unless
the project explicitly supports and requires it.

### Compose and deployment

Validate Compose before changing running services. Run deployment commands with captured exit
codes and redacted output. Avoid destructive Docker commands and commands that remove volumes
or persistent data.

### Health and rollback

Check only services the project uses, using its existing endpoints, timeouts, retries, and
expected responses. A required health failure triggers rollback. Do not claim rollback success
until recovery and post-rollback health checks pass.

### Cleanup

Remove only temporary files and resources created by the run. Never remove volumes, application
or database data, backups, recovery files, logs, or rollback diagnostics.

## Deliverable

Report:

1. Created or modified files.
2. Deployment and failure-handling behavior.
3. Verification commands and results.
4. Project-specific assumptions, unsupported checks, and required configuration.

## Verification

Use mocks or safe test doubles for commands that could change services. Verify:

- stages run in the stated order;
- database readiness occurs before database backup;
- preflight, backup, and Compose validation failures do not roll back;
- deployment and health failures do roll back;
- rollback failures remain nonzero and are reported;
- cleanup preserves persistent data, backups, logs, and recovery files;
- secrets do not appear in terminal or file output; and
- existing project checks still pass.

Report checks that cannot be run instead of claiming they passed.
