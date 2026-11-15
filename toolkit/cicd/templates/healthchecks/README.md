# Health Check Templates

Copy and customize the appropriate healthcheck for your services.

## MySQL

```yaml
healthcheck:
  test: ["CMD", "healthcheck.sh", "--connect", "--innodb_initialized"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

## PostgreSQL

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

## MariaDB

```yaml
healthcheck:
  test: ["CMD", "healthcheck.sh", "--connect", "--innodb_initialized"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

## Redis

```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 10s
```

## MongoDB

```yaml
healthcheck:
  test: ["CMD-SHELL", "mongosh --eval 'db.adminCommand(\"ping\")' --quiet"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

## RabbitMQ

```yaml
healthcheck:
  test: ["CMD-SHELL", "rabbitmq-diagnostics ping"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

## Memcached

```yaml
healthcheck:
  test: ["CMD-SHELL", "echo 'stats' | nc localhost 11211 | grep -q 'STAT'"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 10s
```

## Nginx

```yaml
healthcheck:
  test: ["CMD", "nginx", "-t"]
  interval: 10s
  timeout: 5s
  retries: 3
  start_period: 10s
```