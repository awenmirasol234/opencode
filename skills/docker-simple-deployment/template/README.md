# Simple Docker Deployment Template

This folder is a starting point for one simple application. It is not ready
to run until the runtime, build command, start command, port, and health check
values match the application.

## Copy the template

Copy this folder into the application project. Keep the Docker files at the
project root.

Copy `.env.example` to `.env`, then replace the example values. Keep `.env` out
of Git. Merge the template `.gitignore` rules with an existing project
`.gitignore` instead of replacing that file.

## Customize the Dockerfile

Replace these values in `Dockerfile`:

- `replace-with-runtime-image` with the required runtime image and version.
- `replace-with-build-command` with the existing application build command.
- `8000` with the application's internal port.
- `replace-with-start-command` with the application start command.

Remove the `RUN` line when the application has no build step.

Keep the numeric non-root user when the runtime and application support it.
Make required application directories writable by that user.

The start command uses the Docker JSON array format. For example:

```text
["python", "-m", "app"]
```

## Configure the application

Update `compose.yaml` when the application needs additional environment
variables. Publish only the application port.

Add a health check when the application has a reliable health or readiness
endpoint. Use a command available in the image. Do not assume that `curl` or
`wget` is installed.

## Add a database only when needed

Use both Compose files when the application needs a database:

```text
docker compose -f compose.yaml -f compose.with-db.yaml config
docker compose -f compose.yaml -f compose.with-db.yaml up --build
```

Before running the database setup, replace the database image, data path, and
readiness command in `.env`. Add the environment variables required by the
selected database image to `compose.with-db.yaml`.

The database uses a named volume and does not publish a host port. The app
waits for the database health check before it starts. This is startup ordering;
the application must still handle temporary database failures.

## Verify the deployment

Run configuration validation before starting services:

```text
docker compose config
```

Then confirm that the application becomes healthy, responds on its published
port, and completes one representative workflow. When a database is used,
also verify connectivity and persistence after a restart.
