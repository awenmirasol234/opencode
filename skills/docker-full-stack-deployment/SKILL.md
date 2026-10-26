---
name: docker-full-stack-deployment
description: Containerize and deploy full-stack applications with Docker Compose, Nginx, private networking, and safe environment configuration.
---

# Docker Full-Stack Deployment

Apply this skill when you add or review Docker deployment for a full-stack application.

## Workflow

### 1. Inspect the application

- Identify the frontend, backend, database, runtime versions, package manager, build and start commands, ports, migrations, health endpoints, required services, environment variables, and secrets.

### 2. Document configuration

- Add or update a committed `.env.example` with required and optional variables.
- Keep real `.env` files, credentials, tokens, certificates, and private keys out of Git.
- Never put secrets in Dockerfiles, image layers, frontend code, or build arguments.

### 3. Create only the required services

- Define separate services for `nginx`, `frontend`, `backend`, `db`, and other required dependencies when needed.
- Serve a static SPA from an Nginx frontend build stage instead of adding a redundant frontend runtime container.

### 4. Create simple Dockerfiles

- Use multi-stage builds, narrow build contexts, non-root runtime users where supported, and existing project commands.
- Add `.dockerignore` rules for dependencies, build output, local environment files, and secrets.

### 5. Configure Compose networking and ports

- Use descriptive service names and the default Compose project name.
- Connect services through the Compose network by using service names, not `localhost`; for example, connect the backend to `db:5432`.
- Publish only Nginx's port to the host.
- Do not publish backend, database, cache, worker, or admin ports.
- Do not set `container_name`.
- Use framework-default internal ports where possible.

### 6. Use Nginx as the only entry point

- Serve frontend assets from Nginx or proxy requests to an internal frontend runtime.
- Proxy `/api/` to `backend`.
- Do not expose database routes or private service names.
- For a client-side routed SPA served by Nginx, keep the `/api/` location more specific than the SPA fallback:

  ```nginx
  location / {
      try_files $uri $uri/ /index.html;
  }
  ```

### 7. Add readiness checks

- Add health checks for the database and application services when reliable checks exist.
- Use native database checks or application `/health` or `/ready` endpoints.
- When a database is used, wait until its initialization has completely finished and its readiness check succeeds before creating a backup.
- Stop deployment if database readiness is not reached.
- Make checks compatible with the image; do not assume `curl` or `wget` exists.
- Use Compose readiness conditions where needed:

  ```yaml
  depends_on:
    db:
      condition: service_healthy
  ```

- Treat `depends_on` as startup ordering, not recovery.
- Make applications handle temporary dependency failures.
- Run migrations with the project's supported command and fail clearly when they fail.

### 8. Keep deployment configuration focused

- Provide only Dockerfiles, `compose.yaml`, Nginx configuration, `.dockerignore`, `.env.example`, and brief deployment documentation unless the project needs more.
- Keep Docker setup files comment-free.
- Use clear names and structure.
- Do not add services, scripts, or orchestration features without a clear need.

### 9. Verify the complete stack

- Confirm that `docker compose config` reports no missing variables, accidental ports, or exposed secrets.
- Confirm that all expected containers start and become healthy.
- Verify backend migrations and database connectivity through the Compose service name.
- Verify that frontend pages and static assets load through the Nginx host port.
- Verify that `/api/` reaches the backend through Nginx.
- Verify that SPA deep links work after a direct browser refresh when applicable.
- Complete a representative application workflow through Nginx.
- Confirm that only the Nginx host port is published.

Report every check that you could not run. Do not claim deployment verification from YAML validation alone.

## Verification checklist

- [ ] Document required and optional configuration in `.env.example`.
- [ ] Exclude real secrets from source control and images.
- [ ] Use Compose DNS names and internal ports for services.
- [ ] Expose only Nginx to the host.
- [ ] Persist database data without providing direct host access.
- [ ] Serve or route frontend pages through Nginx and proxy API requests.
- [ ] Configure SPA fallback when required.
- [ ] Configure health checks and readiness conditions where applicable.
- [ ] Confirm that database initialization completes before database backups are created.
- [ ] Test the complete stack and one representative workflow.
