---
name: docker-full-stack-deployment
description: Containerize and deploy full-stack applications with Docker Compose, Nginx, private networking, and safe environment configuration.
---

# Docker Full-Stack Deployment

Use this skill when adding or reviewing Docker deployment for a full-stack application.

## Workflow

1. **Inspect the application first.** Identify the frontend, backend, database, runtime versions, package manager, build and start commands, ports, migrations, health endpoints, required services, environment variables, and secrets.

2. **Document configuration.** Add or update a committed `.env.example` with required and optional variables. Keep real `.env` files, credentials, tokens, certificates, and private keys out of Git. Never put secrets in Dockerfiles, image layers, frontend code, or build arguments.

3. **Create only the required services.** Use separate services for `nginx`, `frontend`, `backend`, `db`, and other required dependencies when they are needed. A static SPA may use a frontend build stage with Nginx serving the output instead of a redundant frontend runtime container.

4. **Use simple Dockerfiles.** Prefer multi-stage builds, narrow build contexts, non-root runtime users where supported, and existing project commands. Add `.dockerignore` rules for dependencies, build output, local environment files, and secrets.

5. **Configure Compose networking and ports.** Use descriptive service names and the default Compose project name. Services communicate through the Compose network using service names, not `localhost`; for example, the backend connects to `db:5432`. Publish only Nginx's port to the host. Do not publish backend, database, cache, worker, or admin ports, and do not use `container_name`.

   Use framework-default internal ports where possible.

6. **Use Nginx as the only entry point.** Nginx serves frontend assets or proxies requests to an internal frontend runtime, and proxies `/api/` to `backend`. Do not expose database routes or private service names.

   For a client-side routed SPA served by Nginx, keep the `/api/` location more specific than the SPA fallback:

   ```nginx
   location / {
       try_files $uri $uri/ /index.html;
   }
   ```

7. **Add readiness checks.** Add health checks for the database and application services when reliable checks exist. Use native database checks or application `/health` or `/ready` endpoints. Make checks compatible with the image; do not assume `curl` or `wget` exists.

   Use Compose readiness conditions where needed:

   ```yaml
   depends_on:
     db:
       condition: service_healthy
   ```

   `depends_on` controls startup order, not recovery. Applications must still handle temporary dependency failures. Run migrations using the project's supported command and fail clearly if they fail.

8. **Keep deployment configuration focused.** Normally provide only Dockerfiles, `compose.yaml`, Nginx configuration, `.dockerignore`, `.env.example`, and brief deployment documentation. Keep Docker setup files comment-free; use clear names and structure instead. Do not add services, scripts, or orchestration features without a clear need.

9. **Verify the complete stack.** Run the following checks:

   - `docker compose config` has no missing variables, accidental ports, or exposed secrets.
   - All expected containers start and become healthy.
   - Backend migrations and database connectivity work through the Compose service name.
   - Frontend pages and static assets load through the Nginx host port.
   - `/api/` reaches the backend through Nginx.
   - SPA deep links work after a direct browser refresh when applicable.
   - A representative application workflow succeeds through Nginx.
   - Only the Nginx host port is published.

   Report checks that could not run. Do not claim the deployment is verified from YAML validation alone.

## Verification checklist

- [ ] `.env.example` documents required and optional configuration.
- [ ] Real secrets are excluded from source control and images.
- [ ] Services use Compose DNS names and internal ports.
- [ ] Only Nginx is exposed to the host.
- [ ] The database has persistence and no direct host access.
- [ ] Nginx serves or routes frontend pages and proxies API requests.
- [ ] SPA fallback is configured when required.
- [ ] Health checks and readiness conditions are configured where applicable.
- [ ] The complete stack and one representative workflow were tested.
