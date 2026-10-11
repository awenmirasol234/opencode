---
name: docker-simple-deployment
description: Containerize and run simple single-service applications with Docker and an optional Compose database.
---

# Docker Simple Deployment

Use this skill when adding or reviewing Docker deployment for a simple application with one service and an optional database.

Do not use this skill for frontend/backend/Nginx stacks. Use `docker-full-stack-deployment` for those. Do not create a Python deployment runner. Use `docker-deployment-automation` for that.

## Workflow

1. **Inspect the application first.** Identify the runtime version, package manager, build and start commands, port, health endpoint, environment variables, secrets, and whether persistence is required.

2. **Document configuration.** Add or update a committed `.env.example` with required and optional variables. Keep real `.env` files, credentials, tokens, certificates, and private keys out of Git. Never put secrets in Dockerfiles, image layers, frontend code, or build arguments.

3. **Create one service.** Use a single `app` service. Add a `db` service only when the project requires a database. Do not add Nginx, workers, caches, or admin tools without a clear need.

4. **Use a simple Dockerfile.** Prefer a multi-stage build when a build step is required, a narrow build context, a non-root runtime user where supported, and existing project commands. Add `.dockerignore` rules for dependencies, build output, local environment files, and secrets.

5. **Configure ports and persistence.** Use the framework-default internal port where possible. Publish only the `app` port to the host. Do not publish the database port and do not use `container_name`. Add a named volume for database data or other required persistence.

6. **Add readiness checks.** Add a health check for the application when a reliable `/health` or `/ready` endpoint exists, and use a native database check when a `db` service exists. Make checks compatible with the image; do not assume `curl` or `wget` exists. `depends_on` controls startup order, not recovery. The application must still handle temporary database failures.

7. **Keep deployment configuration focused.** Normally provide only a Dockerfile, `compose.yaml`, `.dockerignore`, `.env.example`, and brief run documentation. Keep Docker setup files comment-free; use clear names and structure instead.

8. **Verify the deployment.** Run the following checks:

   - `docker compose config` has no missing variables, accidental ports, or exposed secrets.
   - All expected containers start and become healthy.
   - The application responds on the published host port.
   - Database connectivity and persistence work when a `db` service exists.
   - A representative application workflow succeeds.

   Report checks that could not run. Do not claim the deployment is verified from YAML validation alone.

## Verification checklist

- [ ] `.env.example` documents required and optional configuration.
- [ ] Real secrets are excluded from source control and images.
- [ ] Only the `app` port is published to the host.
- [ ] The database has persistence and no direct host access when present.
- [ ] Health checks are configured where applicable.
- [ ] The deployment and one representative workflow were tested.
