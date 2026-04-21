"""
Low-level Binance Futures Testnet client.
Handles authentication (HMAC-SHA256), request signing, and HTTP transport.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests

logger = logging.getLogger("trading_bot.client")

BASE_URL = "https://testnet.binancefuture.com"
_DEFAULT_TIMEOUT = 10  # seconds


class BinanceAPIError(Exception):
    """Raised when the Binance API returns a non-2xx response or an error payload."""

    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"Binance API error {code}: {message}")


class BinanceClient:
    """
    Minimal async-free wrapper around the Binance Futures REST API (USDT-M testnet).

    Args:
        api_key:    Your testnet API key.
        api_secret: Your testnet API secret.
        base_url:   Override the base URL (useful for prod vs testnet switching).
        timeout:    HTTP request timeout in seconds.
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = BASE_URL,
        timeout: int = _DEFAULT_TIMEOUT,
    ) -> None:
        if not api_key or not api_secret:
            raise ValueError("api_key and api_secret must not be empty.")
        self._api_key = api_key
        self._api_secret = api_secret.encode()
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers.update(
            {
                "X-MBX-APIKEY": self._api_key,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )
        logger.debug("BinanceClient initialised with base_url=%s", self._base_url)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _sign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Append timestamp + HMAC-SHA256 signature to *params* (in-place) and return it."""
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(self._api_secret, query_string.encode(), hashlib.sha256).hexdigest()
        params["signature"] = signature
        return params

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Parse the JSON response and raise BinanceAPIError on failure."""
        logger.debug(
            "HTTP %s %s → status=%d body=%s",
            response.request.method,
            response.url,
            response.status_code,
            response.text[:500],
        )
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            return {}

        if isinstance(data, dict) and "code" in data and data["code"] != 200:
            raise BinanceAPIError(data["code"], data.get("msg", "Unknown error"))

        if not response.ok:
            raise BinanceAPIError(response.status_code, response.text)

        return data

    # ------------------------------------------------------------------
    # Public API methods
    # ------------------------------------------------------------------

    def get_server_time(self) -> Dict[str, Any]:
        """Ping the server and return its time (connectivity check)."""
        url = f"{self._base_url}/fapi/v1/time"
        logger.debug("GET %s", url)
        resp = self._session.get(url, timeout=self._timeout)
        return self._handle_response(resp)

    def get_exchange_info(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Fetch exchange info (symbol filters, precision, etc.)."""
        url = f"{self._base_url}/fapi/v1/exchangeInfo"
        params = {}
        if symbol:
            params["symbol"] = symbol
        logger.debug("GET %s params=%s", url, params)
        resp = self._session.get(url, params=params, timeout=self._timeout)
        return self._handle_response(resp)

    def place_order(self, **params: Any) -> Dict[str, Any]:
        """
        POST /fapi/v1/order — place a futures order.

        Commonly used kwargs:
            symbol, side, type, quantity, price, timeInForce,
            stopPrice, reduceOnly, positionSide, newClientOrderId
        """
        url = f"{self._base_url}/fapi/v1/order"
        signed = self._sign(dict(params))
        logger.info(
            "Placing order → symbol=%s side=%s type=%s qty=%s price=%s",
            params.get("symbol"),
            params.get("side"),
            params.get("type"),
            params.get("quantity"),
            params.get("price", "MARKET"),
        )
        logger.debug("POST %s payload=%s", url, signed)
        resp = self._session.post(url, data=signed, timeout=self._timeout)
        result = self._handle_response(resp)
        logger.info("Order response → %s", result)
        return result

    def get_open_orders(self, symbol: Optional[str] = None) -> Any:
        """Fetch all open orders, optionally filtered by symbol."""
        url = f"{self._base_url}/fapi/v1/openOrders"
        params: Dict[str, Any] = {}
        if symbol:
            params["symbol"] = symbol
        signed = self._sign(params)
        logger.debug("GET %s params=%s", url, signed)
        resp = self._session.get(url, params=signed, timeout=self._timeout)
        return self._handle_response(resp)

    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """Cancel an open order by orderId."""
        url = f"{self._base_url}/fapi/v1/order"
        params = self._sign({"symbol": symbol, "orderId": order_id})
        logger.info("Cancelling order orderId=%d symbol=%s", order_id, symbol)
        logger.debug("DELETE %s params=%s", url, params)
        resp = self._session.delete(url, params=params, timeout=self._timeout)
        return self._handle_response(resp)

    def get_account(self) -> Dict[str, Any]:
        """Return account balance and position information."""
        url = f"{self._base_url}/fapi/v2/account"
        params = self._sign({})
        logger.debug("GET %s", url)
        resp = self._session.get(url, params=params, timeout=self._timeout)
        return self._handle_response(resp)
