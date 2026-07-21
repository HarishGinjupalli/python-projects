"""
estimator.py
Core effort-estimation and costing engine.

Given a list of client requirements (role + complexity per requirement) and
a RateCard, this module calculates:
- person-days per requirement (base effort x complexity multiplier)
- cost per requirement (person-days x daily rate)
- a risk-buffered, overhead-adjusted grand total

This is intentionally pure/stateless: pass in data, get back structured
results. Makes it trivial to unit test and to swap the input source
(CSV today, could be a DB or API later) without touching this logic.
"""

from dataclasses import dataclass
from typing import List
import pandas as pd

from src.config_manager import RateCard


class EstimationError(Exception):
    """Raised when input requirement data can't be estimated against the rate card."""


@dataclass
class RequirementEstimate:
    requirement_id: str
    description: str
    role: str
    complexity: str
    effort_days: float
    daily_rate: float
    cost: float


@dataclass
class EstimateSummary:
    line_items: List[RequirementEstimate]
    subtotal_effort_days: float
    subtotal_cost: float
    risk_buffer_percent: float
    risk_buffer_cost: float
    overhead_percent: float
    overhead_cost: float
    grand_total: float
    currency: str


def load_requirements(csv_path: str) -> pd.DataFrame:
    """Load and lightly validate the requirements CSV."""
    df = pd.read_csv(csv_path)

    required_columns = {"requirement_id", "requirement_description", "role", "complexity"}
    missing = required_columns - set(df.columns)
    if missing:
        raise EstimationError(f"Requirements CSV is missing columns: {missing}")

    if df.empty:
        raise EstimationError("Requirements CSV has no rows to estimate")

    return df


def estimate_requirement(row, rate_card: RateCard) -> RequirementEstimate:
    """Compute effort (person-days) and cost for a single requirement row."""
    role = row["role"]
    complexity = row["complexity"]

    if role not in rate_card.roles:
        raise EstimationError(
            f"Unknown role '{role}' in requirement '{row['requirement_id']}'. "
            f"Add it to rate_card.yaml or fix the input data."
        )
    if complexity not in rate_card.complexity_multiplier:
        raise EstimationError(
            f"Unknown complexity '{complexity}' in requirement '{row['requirement_id']}'. "
            f"Valid values: {list(rate_card.complexity_multiplier.keys())}"
        )

    multiplier = rate_card.complexity_multiplier[complexity]
    effort_days = round(rate_card.base_effort_days * multiplier, 2)
    daily_rate = rate_card.roles[role]
    cost = round(effort_days * daily_rate, 2)

    return RequirementEstimate(
        requirement_id=row["requirement_id"],
        description=row["requirement_description"],
        role=role,
        complexity=complexity,
        effort_days=effort_days,
        daily_rate=daily_rate,
        cost=cost,
    )


def build_estimate(df: pd.DataFrame, rate_card: RateCard) -> EstimateSummary:
    """Run estimate_requirement across all rows and roll up totals with risk buffer + overhead."""
    line_items = [estimate_requirement(row, rate_card) for _, row in df.iterrows()]

    subtotal_effort_days = round(sum(item.effort_days for item in line_items), 2)
    subtotal_cost = round(sum(item.cost for item in line_items), 2)

    risk_buffer_cost = round(subtotal_cost * (rate_card.risk_buffer_percent / 100), 2)
    cost_with_risk = subtotal_cost + risk_buffer_cost

    overhead_cost = round(cost_with_risk * (rate_card.overhead_percent / 100), 2)
    grand_total = round(cost_with_risk + overhead_cost, 2)

    return EstimateSummary(
        line_items=line_items,
        subtotal_effort_days=subtotal_effort_days,
        subtotal_cost=subtotal_cost,
        risk_buffer_percent=rate_card.risk_buffer_percent,
        risk_buffer_cost=risk_buffer_cost,
        overhead_percent=rate_card.overhead_percent,
        overhead_cost=overhead_cost,
        grand_total=grand_total,
        currency=rate_card.currency,
    )
