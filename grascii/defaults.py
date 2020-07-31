
from configparser import ConfigParser
from pathlib import Path

from grascii.config import CONF_DIRECTORY, CONF_FILE_NAME

_CONFIG = ConfigParser()
_CONFIG.read_file(Path(__file__).with_name("defaults.conf").open())
_CONFIG.read(Path(CONF_DIRECTORY, CONF_FILE_NAME))

SEARCH = _CONFIG["Search"]
BUILD = _CONFIG["Build"]
