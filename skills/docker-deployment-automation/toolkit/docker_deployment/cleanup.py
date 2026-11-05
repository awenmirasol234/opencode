import shutil

from .config import path_inside_project, project_directory, project_path


def _inside(path, parent):
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _protected(path, protected_paths):
    for protected_path in protected_paths:
        if _inside(path, protected_path) or _inside(protected_path, path):
            return True
    return False


def clean(config, logger):
    # Never remove backups or logs needed after a failure.
    project_dir = project_directory(config)
    backup_dir = project_path(config, config.get("backup_dir", "backups"))
    log_dir = project_path(config, config.get("log_dir", "logs"))
    protected_paths = [
        backup_dir,
        log_dir,
        project_path(config, ".deployment"),
    ]
    for value in config.get("protected_paths", []):
        protected_paths.append(project_path(config, value))
    errors = []

    for value in config.get("temporary_paths", []):
        path = project_path(config, value)
        if not path_inside_project(config, path):
            errors.append("The cleanup path is outside the project: {0}.".format(value))
            continue
        if path == project_dir:
            errors.append("The project directory cannot be removed.")
            continue
        if _protected(path, protected_paths):
            logger.warning("The protected cleanup path was preserved: {0}.".format(value))
            continue
        if not path.exists():
            continue
        try:
            if path.is_symlink():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            logger.ok("The temporary resource was removed: {0}.".format(value))
        except OSError as error:
            errors.append("The temporary resource could not be removed: {0}.".format(error))

    if errors:
        for error in errors:
            logger.fail(error)
        return {"ok": False, "errors": errors}
    logger.success("Safe cleanup completed successfully.")
    return {"ok": True, "errors": []}
