"""
This module parses conf.yaml
"""
import os
import re

try:
    import yaml
except ModuleNotFoundError as error:
    raise ModuleNotFoundError(
        "Please install the module PyYAML using pip: \n pip install PyYAML"
    ) from error

from konsave.consts import HOME, CONFIG_DIR, SHARE_DIR, BIN_DIR


def ends_with(value, path, token) -> str:
    """Finds folder with name ending with the provided value in
    the given path.

    Args:
        value: the value of ENDS_WITH
        path: path
        token: The full token matched in the path (ex. ${ENDS_WITH='.default-release'})
    """
    dirs = os.listdir(path[0:token])
    for directory in dirs:
        if directory.endswith(value):
            return path.replace(token, directory)
    return token


def begins_with(value, path, token) -> str:
    """Finds folder with name beginning with the provided string.

    Args:
        value: the value of BEGINS_WITH
        path: path
        token: The full token matched in the path (ex. ${ENDS_WITH='.default-release'})
    """
    dirs = os.listdir(path[0:token])
    for directory in dirs:
        if directory.startswith(value):
            return path.replace(token, directory)
    return token


def _parse_keywords(parsed, tokens=None):
    """Replaces keywords with values in conf.yaml. For example,
    it will replace, $HOME with /home/username/

    Args:
        parsed: the parsed conf.yaml file
        tokens: the token dictionary
    """
    tokens = tokens or TOKENS
    for item in parsed:
        for name in parsed[item]:
            for key, value in tokens["keywords"].items():
                word = TOKEN_SYMBOL + key
                location = parsed[item][name]["location"]
                if word in location:
                    parsed[item][name]["location"] = location.replace(word, value)


def _parse_functions(parsed, tokens=None):
    """Replaces functions with values in conf.yaml. For example, it will replace,
    ${ENDS_WITH='text'} with a folder whose name ends with "text"

    Args:
        parsed: the parsed conf.yaml file
        tokens: the token dictionary
    """
    tokens = tokens or TOKENS

    for item in parsed:
        for name in parsed[item]:
            location = parsed[item][name]["location"]
            occurences = FUNC_RE.findall(location)
            if not occurences:
                continue
            for token, func, value in occurences:
                if func in tokens["functions"]:
                    parsed[item][name]["location"] = tokens["functions"][func](
                        value, location, token
                    )


def parse(config_file: str):
    """Parse and return the config given a file path

    Args:
        config_file: Path to the config file

    Returns:
        Dict
    """
    with open(config_file, "r", encoding="utf-8") as text:
        konsave_config = yaml.load(text.read(), Loader=yaml.SafeLoader)
    _parse_keywords(konsave_config)
    _parse_functions(konsave_config)
    return konsave_config


TOKEN_SYMBOL = "$"
FUNC_RE = re.compile(rf"\{TOKEN_SYMBOL}\{{(\w+)\=(?:\"|')(\S+)(?:\"|')\}}")
TOKENS = {
    "keywords": {
        "HOME": HOME,
        "CONFIG_DIR": CONFIG_DIR,
        "SHARE_DIR": SHARE_DIR,
        "BIN_DIR": BIN_DIR,
    },
    "functions": {
        "ENDS_WITH": ends_with,
        "BEGINS_WITH": begins_with,
    },
}
