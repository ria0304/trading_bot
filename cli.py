#!/usr/bin/env python3
"""
cli.py — Command-line entry point for the Binance Futures Trading Bot.

Usage examples:
  python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
  python cli.py place --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 95000
  python cli.py place --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --stop-price 90000
  python cli.py account
  python cli.py open-orders --symbol BTCUSDT
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap

from bot.client import BinanceClient, BinanceAPIError
from bot.logging_config import setup_logging
from bot.orders import place_order


# ── Colours (gracefully disabled if not a TTY) ─────────────────────────────

class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    GREEN  = "\033[92m"
    RED    = "\033[91m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"
    DIM    = "\033[2m"

    @staticmethod
    def strip(text: str) -> str:
        import re
        return re.sub(r"\033\[[0-9;]*m", "", text)


def _c(text: str, *codes: str) -> str:
    """Apply ANSI colour codes only when stdout is a TTY."""
    if not sys.stdout.isatty():
        return text
    return "".join(codes) + text + C.RESET


def _banner() -> None:
    print(_c("━" * 56, C.DIM))
    print(_c("  ⚡ Binance Futures Testnet Trading Bot", C.BOLD, C.CYAN))
    print(_c("━" * 56, C.DIM))


def _print_order_summary(args: argparse.Namespace) -> None:
    """Print the order request summary before sending."""
    print()
    print(_c("  ORDER REQUEST", C.BOLD))
    print(_c("  ─────────────────────────────────────", C.DIM))
    rows = [
        ("Symbol",     args.symbol.upper()),
        ("Side",       args.side.upper()),
        ("Type",       args.type.upper()),
        ("Quantity",   args.quantity),
    ]
    if hasattr(args, "price") and args.price:
        rows.append(("Price", args.price))
    if hasattr(args, "stop_price") and args.stop_price:
        rows.append(("Stop Price", args.stop_price))
    for label, value in rows:
        print(f"  {_c(label + ':', C.DIM):<28}{_c(str(value), C.BOLD)}")
    print()


def _print_order_result(result) -> None:
    """Pretty-print the OrderResult dataclass."""
    if result.success:
        print(_c("  ✅  ORDER PLACED SUCCESSFULLY", C.GREEN, C.BOLD))
        print(_c("  ─────────────────────────────────────", C.DIM))
        rows = [
            ("Order ID",      result.order_id),
            ("Client OID",    result.client_order_id),
            ("Symbol",        result.symbol),
            ("Side",          result.side),
            ("Type",          result.order_type),
            ("Status",        result.status),
            ("Orig Qty",      result.orig_qty),
            ("Executed Qty",  result.executed_qty),
            ("Avg Price",     result.avg_price or "N/A"),
            ("Limit Price",   result.price or "N/A"),
        ]
        for label, value in rows:
            if value is not None:
                print(f"  {_c(label + ':', C.DIM):<28}{value}")
    else:
        print(_c("  ❌  ORDER FAILED", C.RED, C.BOLD))
        print(_c("  ─────────────────────────────────────", C.DIM))
        print(f"  {_c('Error:', C.DIM):<28}{_c(result.error or 'Unknown error', C.RED)}")
    print()


# ── Sub-command handlers ────────────────────────────────────────────────────

def cmd_place(client: BinanceClient, args: argparse.Namespace) -> int:
    """Handle the 'place' sub-command."""
    _print_order_summary(args)

    result = place_order(
        client=client,
        symbol=args.symbol,
        side=args.side,
        order_type=args.type,
        quantity=args.quantity,
        price=getattr(args, "price", None),
        stop_price=getattr(args, "stop_price", None),
    )

    _print_order_result(result)
    return 0 if result.success else 1


def cmd_account(client: BinanceClient, _args: argparse.Namespace) -> int:
    """Handle the 'account' sub-command — show USDT balance."""
    try:
        data = client.get_account()
        assets = [a for a in data.get("assets", []) if float(a.get("walletBalance", 0)) > 0]
        print()
        print(_c("  ACCOUNT BALANCES", C.BOLD))
        print(_c("  ─────────────────────────────────────", C.DIM))
        for asset in assets:
            print(
                f"  {_c(asset['asset'] + ':', C.DIM):<28}"
                f"wallet={asset['walletBalance']}  "
                f"unrealisedPnL={asset.get('unrealizedProfit', '0')}"
            )
        if not assets:
            print("  No non-zero balances found.")
        print()
        return 0
    except BinanceAPIError as exc:
        print(_c(f"  ❌  API Error: {exc}", C.RED))
        return 1


def cmd_open_orders(client: BinanceClient, args: argparse.Namespace) -> int:
    """Handle the 'open-orders' sub-command."""
    try:
        symbol = getattr(args, "symbol", None)
        orders = client.get_open_orders(symbol=symbol)
        print()
        print(_c(f"  OPEN ORDERS{' for ' + symbol if symbol else ''}", C.BOLD))
        print(_c("  ─────────────────────────────────────", C.DIM))
        if not orders:
            print("  No open orders.")
        else:
            print(json.dumps(orders, indent=2))
        print()
        return 0
    except BinanceAPIError as exc:
        print(_c(f"  ❌  API Error: {exc}", C.RED))
        return 1


# ── Argument parser ─────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description=textwrap.dedent("""\
            Binance Futures Testnet Trading Bot
            ───────────────────────────────────
            Place MARKET, LIMIT, and STOP_MARKET orders on the USDT-M testnet.
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Global options
    parser.add_argument(
        "--api-key",
        default=os.getenv("BINANCE_API_KEY"),
        help="Binance Futures Testnet API key (or set BINANCE_API_KEY env var)",
    )
    parser.add_argument(
        "--api-secret",
        default=os.getenv("BINANCE_API_SECRET"),
        help="Binance Futures Testnet API secret (or set BINANCE_API_SECRET env var)",
    )
    parser.add_argument(
        "--log-file",
        default="trading_bot.log",
        help="Log file name inside ./logs/ (default: trading_bot.log)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # ── place ──
    place_p = subparsers.add_parser("place", help="Place a new order")
    place_p.add_argument("--symbol",     required=True, help="Trading pair, e.g. BTCUSDT")
    place_p.add_argument("--side",       required=True, choices=["BUY", "SELL", "buy", "sell"],
                         help="Order side: BUY or SELL")
    place_p.add_argument("--type",       required=True,
                         choices=["MARKET", "LIMIT", "STOP_MARKET",
                                  "market", "limit", "stop_market"],
                         help="Order type: MARKET, LIMIT, or STOP_MARKET")
    place_p.add_argument("--quantity",   required=True, type=float, help="Order quantity (base asset)")
    place_p.add_argument("--price",      type=float, default=None,
                         help="Limit price (required for LIMIT orders)")
    place_p.add_argument("--stop-price", type=float, default=None, dest="stop_price",
                         help="Stop trigger price (required for STOP_MARKET orders)")

    # ── account ──
    subparsers.add_parser("account", help="Show account balances")

    # ── open-orders ──
    oo_p = subparsers.add_parser("open-orders", help="List open orders")
    oo_p.add_argument("--symbol", default=None, help="Filter by symbol (optional)")

    return parser


# ── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    logger = setup_logging(log_file=args.log_file)
    logger.debug("CLI args: %s", vars(args))

    _banner()

    # Resolve credentials
    api_key    = args.api_key
    api_secret = args.api_secret

    if not api_key or not api_secret:
        print(_c(
            "\n  ❌  Missing API credentials.\n"
            "      Set BINANCE_API_KEY and BINANCE_API_SECRET environment variables,\n"
            "      or pass --api-key / --api-secret on the command line.\n",
            C.RED,
        ))
        sys.exit(1)

    try:
        client = BinanceClient(api_key=api_key, api_secret=api_secret)
        # Quick connectivity check
        client.get_server_time()
        logger.info("Connected to Binance Futures Testnet ✓")
    except Exception as exc:
        print(_c(f"\n  ❌  Cannot connect to Binance Testnet: {exc}\n", C.RED))
        logger.error("Connection failed: %s", exc)
        sys.exit(1)

    dispatch = {
        "place":       cmd_place,
        "account":     cmd_account,
        "open-orders": cmd_open_orders,
    }

    handler = dispatch.get(args.command)
    if handler is None:
        parser.print_help()
        sys.exit(1)

    sys.exit(handler(client, args))


if __name__ == "__main__":
    main()
