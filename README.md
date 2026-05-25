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
