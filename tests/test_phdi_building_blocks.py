import toml

from phdi import __version__
from pathlib import Path


def test_version():
    with open(Path(__file__).parent.parent / "pyproject.toml") as project_config_file:
        project_config = toml.load(project_config_file)
        assert __version__ == project_config["tool"]["poetry"]["version"]
