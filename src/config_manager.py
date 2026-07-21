"""
config_manager.py
Loads and validates the YAML configuration files that drive the estimator:
- rate_card.yaml : roles, rates, complexity multipliers, risk buffer
- config.yaml    : company/proposal metadata

Keeping this as a dedicated module means the rest of the codebase never
touches YAML directly and always gets validated, typed config back.
"""

from dataclasses import dataclass, field
from typing import Dict, List
import yaml
import os


class ConfigError(Exception):
    """Raised when a config file is missing required keys or has bad values."""


@dataclass
class RateCard:
    currency: str
    roles: Dict[str, float]
    complexity_multiplier: Dict[str, float]
    base_effort_days: float
    risk_buffer_percent: float
    overhead_percent: float


@dataclass
class ProjectConfig:
    company_name: str
    prepared_by: str
    proposal_validity_days: int
    proposal_terms: List[str] = field(default_factory=list)
    output_dir: str = "output"
    log_file: str = "output/run.log"


def load_rate_card(path: str) -> RateCard:
    """Load and validate the rate card YAML file."""
    if not os.path.exists(path):
        raise ConfigError(f"Rate card file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    required_keys = [
        "currency",
        "roles",
        "complexity_multiplier",
        "base_effort_days",
        "risk_buffer_percent",
    ]
    missing = [k for k in required_keys if k not in raw]
    if missing:
        raise ConfigError(f"rate_card.yaml is missing required keys: {missing}")

    if not raw["roles"]:
        raise ConfigError("rate_card.yaml must define at least one role")

    for role, rate in raw["roles"].items():
        if not isinstance(rate, (int, float)) or rate <= 0:
            raise ConfigError(f"Invalid daily rate for role '{role}': {rate}")

    for level, mult in raw["complexity_multiplier"].items():
        if not isinstance(mult, (int, float)) or mult <= 0:
            raise ConfigError(f"Invalid complexity multiplier for '{level}': {mult}")

    if not (0 <= raw["risk_buffer_percent"] <= 100):
        raise ConfigError("risk_buffer_percent must be between 0 and 100")

    return RateCard(
        currency=raw["currency"],
        roles=raw["roles"],
        complexity_multiplier=raw["complexity_multiplier"],
        base_effort_days=float(raw["base_effort_days"]),
        risk_buffer_percent=float(raw["risk_buffer_percent"]),
        overhead_percent=float(raw.get("overhead_percent", 0)),
    )


def load_project_config(path: str) -> ProjectConfig:
    """Load and validate the general project/company config YAML file."""
    if not os.path.exists(path):
        raise ConfigError(f"Project config file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    required_keys = ["company_name", "prepared_by"]
    missing = [k for k in required_keys if k not in raw]
    if missing:
        raise ConfigError(f"config.yaml is missing required keys: {missing}")

    return ProjectConfig(
        company_name=raw["company_name"],
        prepared_by=raw["prepared_by"],
        proposal_validity_days=int(raw.get("proposal_validity_days", 30)),
        proposal_terms=raw.get("proposal_terms", []),
        output_dir=raw.get("output_dir", "output"),
        log_file=raw.get("log_file", "output/run.log"),
    )
