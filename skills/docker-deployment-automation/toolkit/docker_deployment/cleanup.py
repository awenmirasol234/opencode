import shutil
from pathlib import Path

from .config import project_directory, project_path


def is_inside(path, parent):
    try:
        Path(path).resolve().relative_to(Path(parent).resolve())
        return True
    except ValueError:
        return False


def protected_paths(config):
    paths = [
        project_path(config, config.get("backup_dir", "backups")),
        project_path(config, config.get("log_dir", "logs")),
        project_directory(config) / ".deployment",
    ]
    for value in config.get("protected_paths", []):
        paths.append(project_path(config, value))
    return paths


def is_protected(path, paths):
    for protected in paths:
        if is_inside(path, protected) or is_inside(protected, path):
            return True
    return False


def remove_path(path):
    if path.is_symlink():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def clean(config, logger):
    project_dir = project_directory(config)
    protected = protected_paths(config)
    errors = []
    for value in config.get("temporary_paths", []):
        path = project_dir / value
        if not is_inside(path, project_dir):
            errors.append("The cleanup path is outside the project: {0}.".format(value))
            continue
        if path.resolve() == project_dir:
            errors.append("The project directory cannot be removed.")
            continue
        if is_protected(path, protected):
            logger.warn("The protected path was preserved: {0}.".format(value))
            continue
        if not path.exists():
            continue
        try:
            remove_path(path)
            logger.ok("The temporary path was removed: {0}.".format(value))
        except OSError as error:
            errors.append("The temporary path could not be removed: {0}.".format(error))
    if errors:
        for error in errors:
            logger.fail(error)
        return {"ok": False, "errors": errors}
    logger.ok("The safe cleanup completed successfully.")
    return {"ok": True, "errors": []}
