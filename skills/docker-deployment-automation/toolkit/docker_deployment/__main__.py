import argparse
import importlib.util
from pathlib import Path

from .runner import run


def load_config(path):
    config_path = Path(path).resolve()
    spec = importlib.util.spec_from_file_location("deployment_config", str(config_path))
    if spec is None or spec.loader is None:
        raise ValueError("The configuration file could not be loaded.")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    config = getattr(module, "CONFIG", None)
    if config is None and hasattr(module, "get_config"):
        config = module.get_config()
    if not isinstance(config, dict):
        raise ValueError("The configuration file must define a CONFIG dictionary.")
    return config


def main():
    parser = argparse.ArgumentParser(description="Run a safe Docker Compose deployment.")
    parser.add_argument(
        "--config",
        default="deploy_config.py",
        help="Path to a Python file containing CONFIG.",
    )
    arguments = parser.parse_args()

    try:
        config = load_config(arguments.config)
    except Exception as error:
        print("The deployment configuration could not be loaded: {0}".format(error))
        return 2

    return run(config)


if __name__ == "__main__":
    raise SystemExit(main())
