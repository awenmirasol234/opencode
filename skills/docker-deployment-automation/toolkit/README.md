# Docker Deployment Toolkit

Small Python toolkit for safe Docker Compose deployments.

## When to use this toolkit vs GitHub Actions

| Python Toolkit | GitHub Actions |
| --- | --- |
| Local or remote server runs `python -m docker_deployment` | CI/CD pipeline runs deployments automatically |
| No GitHub account required | Requires GitHub Actions |
| Simpler debugging | Better for team collaboration |
| Use for: local dev, self-hosted runners, custom workflows | Use for: automated prod deployments, PR reviews |

## Quick Start

```bash
python -m pip install ./path/to/toolkit
python -m docker_deployment --config deploy_config.py
```

## Architecture

12-stage deployment pipeline:
1. Initialize logging
2. Acquire deployment lock
3. Run preflight checks
4. Backup preparation hook
5. Start database, wait, create backup
6. Validate Compose
7. Release before deploy hook
8. Pull images, deploy
9. Poll health checks
10. Save deployed SHA
11. Rollback on failure
12. Clean up, report

## Configuration

See `examples/deploy_config.py` for all options.

## Testing

```bash
python -m unittest discover -s toolkit/tests -v
```