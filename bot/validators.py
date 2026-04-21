"""
Input validation for order parameters.
All public functions raise ValueError with a human-readable message on failure.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Optional


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}  # STOP_MARKET = bonus type


def validate_symbol(symbol: str) -> str:
    """Return the upper-cased symbol or raise ValueError."""
    symbol = symbol.strip().upper()
    if not symbol:
        raise ValueError("Symbol must not be empty.")
    if not symbol.isalnum():
        raise ValueError(f"Symbol '{symbol}' contains invalid characters. Use alphanumeric only (e.g. BTCUSDT).")
    return symbol


def validate_side(side: str) -> str:
    """Return the upper-cased side or raise ValueError."""
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(f"Side must be one of {sorted(VALID_SIDES)}, got '{side}'.")
    return side


def validate_order_type(order_type: str) -> str:
    """Return the upper-cased order type or raise ValueError."""
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Order type must be one of {sorted(VALID_ORDER_TYPES)}, got '{order_type}'."
        )
    return order_type


def validate_quantity(quantity: str | float) -> Decimal:
    """Parse and validate quantity; must be a positive number."""
    try:
        qty = Decimal(str(quantity))
    except InvalidOperation:
        raise ValueError(f"Quantity '{quantity}' is not a valid number.")
    if qty <= 0:
        raise ValueError(f"Quantity must be greater than zero, got {qty}.")
    return qty


def validate_price(price: Optional[str | float], order_type: str) -> Optional[Decimal]:
    """
    Parse and validate price.

    - LIMIT and STOP_MARKET orders require a positive price.
    - MARKET orders must not supply a price.
    """
    order_type = order_type.strip().upper()
    if order_type == "MARKET":
        if price is not None:
            raise ValueError("MARKET orders do not accept a price parameter.")
        return None

    # LIMIT / STOP_MARKET require price
    if price is None:
        raise ValueError(f"{order_type} orders require a --price argument.")
    try:
        p = Decimal(str(price))
    except InvalidOperation:
        raise ValueError(f"Price '{price}' is not a valid number.")
    if p <= 0:
        raise ValueError(f"Price must be greater than zero, got {p}.")
    return p


def validate_stop_price(stop_price: Optional[str | float], order_type: str) -> Optional[Decimal]:
    """Stop price is required for STOP_MARKET orders."""
    order_type = order_type.strip().upper()
    if order_type != "STOP_MARKET":
        return None
    if stop_price is None:
        raise ValueError("STOP_MARKET orders require a --stop-price argument.")
    try:
        sp = Decimal(str(stop_price))
    except InvalidOperation:
        raise ValueError(f"Stop price '{stop_price}' is not a valid number.")
    if sp <= 0:
        raise ValueError(f"Stop price must be greater than zero, got {sp}.")
    return sp
