DOCKER_COMPOSE_COMMAND = ["docker", "compose"]
DOCKER_COMPOSE_LEGACY_COMMAND = ["docker-compose"]
DOCKER_COMPOSE_VERSION_COMMAND = ["docker", "compose", "version"]
DOCKER_COMPOSE_LEGACY_VERSION_COMMAND = ["docker-compose", "version"]
DOCKER_INFO_COMMAND = ["docker", "info"]
DOCKER_IMAGE_INSPECT_COMMAND = ["docker", "image", "inspect"]
DOCKER_INSPECT_COMMAND = ["docker", "inspect"]
CONTAINER_INSPECT_FORMAT = "{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{end}}"

COMPOSE_PS_ARGS = ["ps", "-q"]
COMPOSE_VALIDATE_ARGS = ["config"]
COMPOSE_SERVICES_ARGS = ["config", "--services"]
COMPOSE_PULL_ARGS = ["pull"]
COMPOSE_START_ARGS = ["up", "-d"]
COMPOSE_DEPLOY_ARGS = ["up", "-d"]
COMPOSE_ROLLBACK_ARGS = ["up", "-d"]

DEFAULT_COMPOSE_FILES = ["compose.yaml"]
