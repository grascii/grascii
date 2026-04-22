from __future__ import annotations

from configparser import ConfigParser
from importlib.resources import files

from grascii.config import get_config_file_path

_defaults = files("grascii").joinpath("defaults.conf").read_text()

_CONFIG = ConfigParser()
_CONFIG.read_string(_defaults)
_CONFIG.read(get_config_file_path())

DEFAULTS = ConfigParser()
DEFAULTS.read_string(_defaults)

SEARCH = _CONFIG["Search"]
