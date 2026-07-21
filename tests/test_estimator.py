"""
Unit tests for estimator.py
Covers: single requirement estimate math, full build_estimate rollup,
unknown role/complexity errors, empty CSV handling.
"""

import pandas as pd
import pytest

from src.config_manager import RateCard
from src.estimator import (
    estimate_requirement,
    build_estimate,
    load_requirements,
    EstimationError,
)


@pytest.fixture
def rate_card():
    return RateCard(
        currency="INR",
        roles={"Python Developer": 8000, "Business Analyst": 9500},
        complexity_multiplier={"Low": 1.0, "Medium": 1.5, "High": 2.2},
        base_effort_days=2.0,
        risk_buffer_percent=10,
        overhead_percent=5,
    )


def test_estimate_requirement_basic(rate_card):
    row = pd.Series(
        {
            "requirement_id": "REQ-001",
            "requirement_description": "Build API",
            "role": "Python Developer",
            "complexity": "Medium",
        }
    )
    result = estimate_requirement(row, rate_card)
    # base_effort_days(2.0) * multiplier(1.5) = 3.0 person-days
    assert result.effort_days == 3.0
    # 3.0 days * 8000/day = 24000
    assert result.cost == 24000.0


def test_estimate_requirement_unknown_role(rate_card):
    row = pd.Series(
        {
            "requirement_id": "REQ-002",
            "requirement_description": "Unknown work",
            "role": "Data Scientist",  # not in rate_card
            "complexity": "Low",
        }
    )
    with pytest.raises(EstimationError, match="Unknown role"):
        estimate_requirement(row, rate_card)


def test_estimate_requirement_unknown_complexity(rate_card):
    row = pd.Series(
        {
            "requirement_id": "REQ-003",
            "requirement_description": "Some work",
            "role": "Python Developer",
            "complexity": "Extreme",  # not in rate_card
        }
    )
    with pytest.raises(EstimationError, match="Unknown complexity"):
        estimate_requirement(row, rate_card)


def test_build_estimate_rollup(rate_card):
    df = pd.DataFrame(
        [
            {
                "requirement_id": "REQ-001",
                "requirement_description": "Task A",
                "role": "Python Developer",
                "complexity": "Low",  # 2.0 days * 8000 = 16000
            },
            {
                "requirement_id": "REQ-002",
                "requirement_description": "Task B",
                "role": "Business Analyst",
                "complexity": "Medium",  # 3.0 days * 9500 = 28500
            },
        ]
    )
    summary = build_estimate(df, rate_card)

    assert summary.subtotal_effort_days == 5.0
    assert summary.subtotal_cost == 44500.0

    # risk buffer 10% of 44500 = 4450
    assert summary.risk_buffer_cost == 4450.0

    # cost with risk = 48950; overhead 5% of that = 2447.5
    assert summary.overhead_cost == 2447.5

    # grand total = 48950 + 2447.5 = 51397.5
    assert summary.grand_total == 51397.5
    assert len(summary.line_items) == 2


def test_load_requirements_missing_columns(tmp_path):
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text("id,desc\n1,test\n")
    with pytest.raises(EstimationError, match="missing columns"):
        load_requirements(str(bad_csv))


def test_load_requirements_empty(tmp_path):
    empty_csv = tmp_path / "empty.csv"
    empty_csv.write_text(
        "requirement_id,requirement_description,role,complexity\n"
    )
    with pytest.raises(EstimationError, match="no rows"):
        load_requirements(str(empty_csv))


def test_load_requirements_valid(tmp_path):
    csv_path = tmp_path / "valid.csv"
    csv_path.write_text(
        "requirement_id,requirement_description,role,complexity\n"
        "REQ-001,Test task,Python Developer,Low\n"
    )
    df = load_requirements(str(csv_path))
    assert len(df) == 1
    assert df.iloc[0]["role"] == "Python Developer"
