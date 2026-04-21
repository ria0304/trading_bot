"""
Order placement logic — sits between the CLI and the raw BinanceClient.
Each function validates inputs, builds the correct payload, calls the client,
and returns a normalised OrderResult dataclass.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Dict, Optional

from .client import BinanceClient, BinanceAPIError
from .validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_stop_price,
)

logger = logging.getLogger("trading_bot.orders")


@dataclass
class OrderResult:
    """Normalised view of a Binance order response."""

    success: bool
    order_id: Optional[int] = None
    client_order_id: Optional[str] = None
    symbol: Optional[str] = None
    side: Optional[str] = None
    order_type: Optional[str] = None
    status: Optional[str] = None
    orig_qty: Optional[str] = None
    executed_qty: Optional[str] = None
    avg_price: Optional[str] = None
    price: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "OrderResult":
        return cls(
            success=True,
            order_id=data.get("orderId"),
            client_order_id=data.get("clientOrderId"),
            symbol=data.get("symbol"),
            side=data.get("side"),
            order_type=data.get("type"),
            status=data.get("status"),
            orig_qty=data.get("origQty"),
            executed_qty=data.get("executedQty"),
            avg_price=data.get("avgPrice"),
            price=data.get("price"),
            raw=data,
        )

    @classmethod
    def from_error(cls, error: str) -> "OrderResult":
        return cls(success=False, error=error)


def place_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: str | float,
    price: Optional[str | float] = None,
    stop_price: Optional[str | float] = None,
    time_in_force: str = "GTC",
) -> OrderResult:
    """
    Validate all inputs and place a MARKET, LIMIT, or STOP_MARKET order.

    Args:
        client:        Authenticated BinanceClient instance.
        symbol:        Trading pair, e.g. 'BTCUSDT'.
        side:          'BUY' or 'SELL'.
        order_type:    'MARKET', 'LIMIT', or 'STOP_MARKET'.
        quantity:      Order size (base asset).
        price:         Limit price (required for LIMIT).
        stop_price:    Stop trigger price (required for STOP_MARKET).
        time_in_force: GTC/IOC/FOK (only relevant for LIMIT orders).

    Returns:
        OrderResult dataclass — check .success before using other fields.
    """
    # --- Validation ---
    try:
        symbol = validate_symbol(symbol)
        side = validate_side(side)
        order_type = validate_order_type(order_type)
        qty: Decimal = validate_quantity(quantity)
        lmt_price: Optional[Decimal] = validate_price(price, order_type)
        stp_price: Optional[Decimal] = validate_stop_price(stop_price, order_type)
    except ValueError as exc:
        logger.error("Validation error: %s", exc)
        return OrderResult.from_error(str(exc))

    # --- Build payload ---
    payload: Dict[str, Any] = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": str(qty),
    }

    if order_type == "LIMIT":
        payload["price"] = str(lmt_price)
        payload["timeInForce"] = time_in_force

    if order_type == "STOP_MARKET":
        payload["stopPrice"] = str(stp_price)
        # STOP_MARKET does not need a limit price or timeInForce

    logger.info("Order payload built: %s", payload)

    # --- Execute ---
    try:
        response = client.place_order(**payload)
        result = OrderResult.from_response(response)
        logger.info(
            "Order placed successfully: orderId=%s status=%s executedQty=%s",
            result.order_id,
            result.status,
            result.executed_qty,
        )
        return result
    except BinanceAPIError as exc:
        logger.error("Binance API error while placing order: %s", exc)
        return OrderResult.from_error(str(exc))
    except Exception as exc:
        logger.exception("Unexpected error while placing order: %s", exc)
        return OrderResult.from_error(f"Unexpected error: {exc}")
