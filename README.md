# Binance Futures Trading Bot

> A clean Python CLI for placing orders on Binance Futures 
> USDT-M Testnet — with HMAC signing, input validation, 
> structured logging, and robust error handling.

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Binance](https://img.shields.io/badge/Binance-Futures%20Testnet-yellow)
![Status](https://img.shields.io/badge/Exchange-USDT--M-green)
![License](https://img.shields.io/badge/License-MIT-green)

## What it does
Places MARKET, LIMIT, and STOP_MARKET orders on Binance 
Futures Testnet via direct REST API calls with HMAC-SHA256 
signing — no SDK dependency. Includes full input validation, 
file + console logging, and a clean CLI built with argparse.

## Project structure
 Trading_bot/
├── bot/
│   ├── client.py        # Binance REST API wrapper (HMAC signing)
│   ├── orders.py        # Order placement + OrderResult dataclass
│   ├── validators.py    # Input validation (symbol, side, qty, price)
│   └── logging_config.py
├── cli.py               # CLI entry point (argparse)
├── logs/
│   └── trading_bot.log  # Auto-created on first run
└── requirements.txt
## Setup

### 1. Get testnet credentials
- Visit https://testnet.binancefuture.com
- Sign in → API Key → Generate

### 2. Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Set credentials
```bash
export BINANCE_API_KEY="your_key"
export BINANCE_API_SECRET="your_secret"
```

## Usage

```bash
# Market order
python cli.py place --symbol BTCUSDT --side BUY \
  --type MARKET --quantity 0.001

# Limit order
python cli.py place --symbol BTCUSDT --side SELL \
  --type LIMIT --quantity 0.001 --price 112000

# Stop-loss
python cli.py place --symbol BTCUSDT --side SELL \
  --type STOP_MARKET --quantity 0.001 --stop-price 90000

# Account balances
python cli.py account

# Open orders
python cli.py open-orders --symbol BTCUSDT
```

## Sample output
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ORDER PLACED SUCCESSFULLY
─────────────────────────────────────
Symbol:       BTCUSDT
Side:         BUY
Type:         MARKET
Status:       FILLED
Executed:     0.001 BTC
Avg Price:    107,432.40 USDT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Order types supported
| Type | Description |
|------|-------------|
| `MARKET` | Executes instantly at current price |
| `LIMIT` | Executes at specified price or better |
| `STOP_MARKET` | Triggers market order at stop price |

## Future scope
- Live trading mode (beyond testnet)
- Strategy layer (momentum, mean reversion)
- Backtesting engine with historical data
- P&L tracking and position management
- Telegram / Discord alerts on fill

## Tech stack
`Python` `Binance REST API` `HMAC-SHA256` `argparse` `logging`

## License
MIT — by [ria0304](https://github.com/ria0304)
