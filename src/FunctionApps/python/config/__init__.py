import os


def get_required_config(varname: str, default: str = None) -> str:
    """Grab a required config val and throw an exception if it's not present"""
    if varname not in os.environ:
        if default is None:
            raise Exception(f"Config value {varname} not found in the environment")
        return default
    return os.environ[varname]
