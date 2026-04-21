"""
Logging configuration for the Binance Futures trading bot.
Sets up both file and console handlers with structured formatting.
"""

import logging
import sys
from pathlib import Path


def setup_logging(log_file: str = "trading_bot.log", level: int = logging.DEBUG) -> logging.Logger:
    """
    Configure and return the root logger with file + console handlers.

    Args:
        log_file: Path to the log file (created if it doesn't exist).
        level:    Minimum log level captured by the file handler.

    Returns:
        Configured logger instance named 'trading_bot'.
    """
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / log_file

    logger = logging.getLogger("trading_bot")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    fmt_file = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    fmt_console = logging.Formatter(
        fmt="%(levelname)-8s %(message)s",
    )

    # File handler — verbose (DEBUG+)
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(fmt_file)

    # Console handler — INFO+ only to keep CLI output clean
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt_console)

    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.info("Logging initialised → %s", log_path.resolve())
    return logger
