from __future__ import annotations

from pathlib import Path

import pytest

from grascii.config import (
    CONF_FILE_NAME,
    config_exists,
    create_config,
    delete_config,
    get_config_file_path,
    get_default_config,
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
    create_config()
    assert config_exists()
    assert Path(tmp_config_path, CONF_FILE_NAME).exists()
    assert Path(get_config_file_path()).read_text() == get_default_config()
    delete_config()
    assert not Path(tmp_config_path, CONF_FILE_NAME).exists()
    assert not config_exists()
