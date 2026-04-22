from __future__ import annotations

from configparser import ConfigParser
from pathlib import Path

import pytest

from grascii.config import (
    CONF_FILE_NAME,
    ConfigPreset,
    config_exists,
    create_config,
    delete_config,
    get_config_file_path,
    get_default_config,
    get_preset_config,
)


@pytest.fixture
def tmp_config_path(tmp_path, monkeypatch):
    monkeypatch.setattr("grascii.config.CONF_DIRECTORY", tmp_path)
    return tmp_path


def test_get_config_file_path(tmp_config_path):
    assert get_config_file_path() == tmp_config_path / CONF_FILE_NAME


def test_get_default_config():
    assert Path("grascii/defaults.conf").read_text() == get_default_config()


def test_create_and_delete_config(tmp_config_path):
    assert not config_exists()
    create_config(ConfigPreset.PREANNIVERSARY)
    assert config_exists()
    assert Path(tmp_config_path, CONF_FILE_NAME).exists()
    assert Path(get_config_file_path()).read_text() == get_preset_config(
        ConfigPreset.PREANNIVERSARY
    )
    delete_config()
    assert not Path(tmp_config_path, CONF_FILE_NAME).exists()
    assert not config_exists()


def test_get_preset_config():
    preanniversary_config = get_preset_config(ConfigPreset.PREANNIVERSARY)
    preanniversary_parser = ConfigParser()
    preanniversary_parser.read_string(preanniversary_config)
    assert (
        preanniversary_parser["Search"]["Dictionary"]
        == ":preanniversary :preanniversary-phrases"
    )

    anniversary_config = get_preset_config(ConfigPreset.ANNIVERSARY)
    anniversary_parser = ConfigParser()
    anniversary_parser.read_string(anniversary_config)
    assert anniversary_parser["Search"]["Dictionary"] == ":anniversary"
