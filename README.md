# Binance Futures Testnet Trading Bot

A clean, well-structured Python CLI application for placing orders on the **Binance Futures USDT-M Testnet**.  
Supports `MARKET`, `LIMIT`, and `STOP\_MARKET` order types with full input validation, structured logging, and robust error handling.

\---

## Project Structure

```
trading\_bot/
├── bot/
│   ├── \_\_init\_\_.py
│   ├── client.py          # Binance REST API wrapper (HMAC signing, HTTP)
│   ├── orders.py          # Order placement logic + OrderResult dataclass
│   ├── validators.py      # Input validation (symbol, side, qty, price, …)
│   └── logging\_config.py  # File + console logging setup
├── cli.py                 # CLI entry point (argparse)
├── logs/
│   └── trading\_bot.log    # Auto-created on first run
├── requirements.txt
└── README.md
```

\---

## Setup

### 1\. Get Testnet Credentials

1. Visit [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Sign in 
3. Go to **API Key** → click **Generate**

### 2\. Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

### 3\. Set Credentials

**Option A — Environment variables (recommended):**

```bash
export BINANCE\_API\_KEY="your\_api\_key\_here"
export BINANCE\_API\_SECRET="your\_api\_secret\_here"
```

**Option B — CLI flags:**

```bash
python cli.py --api-key YOUR\_KEY --api-secret YOUR\_SECRET place ...
```

\---

## Usage

### Place a MARKET order

```bash
# Buy 0.001 BTC at market price
python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

# Sell 0.05 ETH at market price
python cli.py place --symbol ETHUSDT --side SELL --type MARKET --quantity 0.05
```

### Place a LIMIT order

```bash
# Sell 0.001 BTC with a limit price of 112,000 USDT (GTC)
python cli.py place --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 112000

# Buy 0.1 ETH at 3,200 USDT
python cli.py place --symbol ETHUSDT --side BUY --type LIMIT --quantity 0.1 --price 3200
```

### Place a STOP\_MARKET order *(bonus)*

```bash
# Stop-loss: sell 0.001 BTC if price drops to 90,000 USDT
python cli.py place --symbol BTCUSDT --side SELL --type STOP\_MARKET --quantity 0.001 --stop-price 90000
```

### View account balances

```bash
python cli.py account
```

### List open orders

```bash
python cli.py open-orders                    # all symbols
python cli.py open-orders --symbol BTCUSDT   # filtered
```

### Use a custom log file

```bash
python cli.py --log-file my\_session.log place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

\---

## Sample Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Binance Futures Testnet Trading Bot
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ORDER REQUEST
  ─────────────────────────────────────
  Symbol:                     BTCUSDT
  Side:                       BUY
  Type:                       MARKET
  Quantity:                   0.001

    ORDER PLACED SUCCESSFULLY
  ─────────────────────────────────────
  Order ID:                   4286427623
  Client OID:                 web\_xKz3pQm19Lv2Hc5rNw8
  Symbol:                     BTCUSDT
  Side:                       BUY
  Type:                       MARKET
  Status:                     FILLED
  Orig Qty:                   0.001
  Executed Qty:               0.001
  Avg Price:                  107432.40000
  Limit Price:                0
```

\---

## 

