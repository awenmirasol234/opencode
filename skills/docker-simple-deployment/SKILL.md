---
name: docker-simple-deployment
description: Containerize and run simple single-service applications with Docker and an optional Compose database.
---

# Docker Simple Deployment

Apply this skill when you add or review Docker deployment for a simple application with one service and an optional database.

Do not apply this skill to frontend/backend/Nginx stacks. Apply `docker-full-stack-deployment` to those stacks. Do not create a Python deployment runner. Apply `docker-deployment-automation` to that work.

## Copyable template

The `template/` folder contains a starting point for simple applications.
Copy it into a project, then replace its runtime, build, start, port, and
health-check placeholders with values from that project.

The default `compose.yaml` contains only the `app` service. Use
`compose.with-db.yaml` together with it only when the project needs a database.
The database image, environment values, data path, and readiness command must
be configured for the selected database. The template does not guess them.

## Workflow

### 1. Inspect the application

- Identify the runtime version, package manager, build and start commands, port, health endpoint, environment variables, secrets, and persistence requirements.

### 2. Document configuration

- Add or update a committed `.env.example` with required and optional variables.
- Keep real `.env` files, credentials, tokens, certificates, and private keys out of Git.
- Never put secrets in Dockerfiles, image layers, frontend code, or build arguments.

### 3. Create one service

- Define a single `app` service.
- Add a `db` service only when the project requires a database.
- Do not add Nginx, workers, caches, or admin tools without a clear need.

### 4. Create a simple Dockerfile

- Use a multi-stage build when a build step is required.
- Use a narrow build context, a non-root runtime user where supported, and existing project commands.
- Add `.dockerignore` rules for dependencies, build output, local environment files, and secrets.

### 5. Configure ports and persistence

- Use the framework-default internal port where possible.
- Publish only the `app` port to the host.
- Do not publish the database port or set `container_name`.
- Add a named volume for database data or other required persistence.

### 6. Add readiness checks

- Add a health check for the application when a reliable `/health` or `/ready` endpoint exists.
- Use a native database check when a `db` service exists.
- When a database is used, wait until its initialization has completely finished and its readiness check succeeds before creating a backup.
- Stop deployment if database readiness is not reached.
- Make checks compatible with the image; do not assume `curl` or `wget` exists.
- Treat `depends_on` as startup ordering, not recovery.
- Make the application handle temporary database failures.

### 7. Keep deployment configuration focused

- Provide only a Dockerfile, `compose.yaml`, optional `compose.with-db.yaml`, `.dockerignore`, `.gitignore`, `.env.example`, and brief run documentation unless the project needs more.
- Keep Docker setup files comment-free.
- Use clear names and structure.

### 8. Verify the deployment

- Confirm that `docker compose config` reports no missing variables, accidental ports, or exposed secrets.
- Confirm that all expected containers start and become healthy.
- Verify that the application responds on the published host port.
- Verify database connectivity and persistence when a `db` service exists.
- Complete a representative application workflow.

Report every check that you could not run. Do not claim deployment verification from YAML validation alone.

## Verification checklist

- [ ] Document required and optional configuration in `.env.example`.
- [ ] Exclude real secrets from source control and images.
- [ ] Publish only the `app` port to the host.
- [ ] Persist database data without providing direct host access when a database exists.
- [ ] Configure health checks where applicable.
- [ ] Confirm that database initialization completes before database backups are created.
- [ ] Test the deployment and one representative workflow.
