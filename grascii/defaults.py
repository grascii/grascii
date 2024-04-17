from __future__ import annotations

from configparser import ConfigParser
from pathlib import Path

from grascii.config import get_config_file_path

_CONFIG = ConfigParser()
_CONFIG.read_file(Path(__file__).with_name("defaults.conf").open())
_CONFIG.read(get_config_file_path())

DEFAULTS = ConfigParser()
DEFAULTS.read_file(Path(__file__).with_name("defaults.conf").open())

SEARCH = _CONFIG["Search"]
