"""
utils.py
Shared helpers: logging setup and small formatting utilities.
"""

import logging
import os


def setup_logger(log_file: str = "output/run.log", name: str = "estimator") -> logging.Logger:
    """
    Configure and return a logger that writes to both console and a log file.
    """
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers if setup_logger is called more than once
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def format_currency(amount: float, currency: str = "INR") -> str:
    """
    Format a number as currency with thousands separators.
    Uses Indian-style grouping for INR, standard grouping otherwise.
    """
    if currency.upper() == "INR":
        return f"₹{_indian_grouping(amount)}"
    return f"{currency} {amount:,.2f}"


def _indian_grouping(amount: float) -> str:
    """
    Format a number using Indian numbering (lakh/crore) comma placement.
    e.g. 1234567.5 -> '12,34,567.50'
    """
    amount = round(amount, 2)
    whole, _, decimal = f"{amount:.2f}".partition(".")
    negative = whole.startswith("-")
    if negative:
        whole = whole[1:]

    if len(whole) <= 3:
        grouped = whole
    else:
        last3 = whole[-3:]
        rest = whole[:-3]
        parts = []
        while len(rest) > 2:
            parts.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            parts.insert(0, rest)
        grouped = ",".join(parts) + "," + last3

    result = f"{grouped}.{decimal}"
    return f"-{result}" if negative else result
