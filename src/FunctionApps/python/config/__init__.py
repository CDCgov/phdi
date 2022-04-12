import os


def get_required_config(varname: str) -> str:
    """Grab a required config val and throw an exception if it's not present"""
    if varname not in os.environ:
        raise Exception(f"Config value {varname} not found in the environment")
    return os.environ[varname]
