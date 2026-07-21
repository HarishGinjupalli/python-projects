"""
Unit tests for config_manager.py
Covers: valid load, missing file, missing keys, invalid rate/multiplier values.
"""

import os
import tempfile
import pytest
import yaml

from src.config_manager import load_rate_card, load_project_config, ConfigError


def write_yaml(tmpdir, filename, data):
    path = os.path.join(tmpdir, filename)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f)
    return path


VALID_RATE_CARD = {
    "currency": "INR",
    "roles": {"Python Developer": 8000},
    "complexity_multiplier": {"Low": 1.0, "Medium": 1.5, "High": 2.2},
    "base_effort_days": 2.0,
    "risk_buffer_percent": 10,
    "overhead_percent": 5,
}

VALID_PROJECT_CONFIG = {
    "company_name": "Test Co",
    "prepared_by": "Tester",
    "proposal_validity_days": 30,
    "proposal_terms": ["Term 1"],
}


def test_load_rate_card_valid(tmp_path):
    path = write_yaml(tmp_path, "rate_card.yaml", VALID_RATE_CARD)
    rate_card = load_rate_card(path)
    assert rate_card.currency == "INR"
    assert rate_card.roles["Python Developer"] == 8000
    assert rate_card.risk_buffer_percent == 10


def test_load_rate_card_missing_file():
    with pytest.raises(ConfigError, match="not found"):
        load_rate_card("nonexistent_file.yaml")


def test_load_rate_card_missing_keys(tmp_path):
    bad = {"currency": "INR"}  # missing roles, multipliers, etc.
    path = write_yaml(tmp_path, "bad_rate_card.yaml", bad)
    with pytest.raises(ConfigError, match="missing required keys"):
        load_rate_card(path)


def test_load_rate_card_no_roles(tmp_path):
    bad = dict(VALID_RATE_CARD)
    bad["roles"] = {}
    path = write_yaml(tmp_path, "bad_rate_card.yaml", bad)
    with pytest.raises(ConfigError, match="at least one role"):
        load_rate_card(path)


def test_load_rate_card_invalid_rate(tmp_path):
    bad = dict(VALID_RATE_CARD)
    bad["roles"] = {"Python Developer": -100}
    path = write_yaml(tmp_path, "bad_rate_card.yaml", bad)
    with pytest.raises(ConfigError, match="Invalid daily rate"):
        load_rate_card(path)


def test_load_rate_card_invalid_risk_buffer(tmp_path):
    bad = dict(VALID_RATE_CARD)
    bad["risk_buffer_percent"] = 150
    path = write_yaml(tmp_path, "bad_rate_card.yaml", bad)
    with pytest.raises(ConfigError, match="risk_buffer_percent"):
        load_rate_card(path)


def test_load_project_config_valid(tmp_path):
    path = write_yaml(tmp_path, "config.yaml", VALID_PROJECT_CONFIG)
    config = load_project_config(path)
    assert config.company_name == "Test Co"
    assert config.proposal_validity_days == 30
    assert config.proposal_terms == ["Term 1"]


def test_load_project_config_missing_keys(tmp_path):
    bad = {"prepared_by": "Tester"}  # missing company_name
    path = write_yaml(tmp_path, "bad_config.yaml", bad)
    with pytest.raises(ConfigError, match="missing required keys"):
        load_project_config(path)


def test_load_project_config_missing_file():
    with pytest.raises(ConfigError, match="not found"):
        load_project_config("nonexistent_config.yaml")
