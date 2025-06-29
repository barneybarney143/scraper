"""
Installation:
    pip install yfinance pandas pyarrow --upgrade
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr
import io
import pandas as pd
import yfinance as yf

START_DATE = "2000-01-01"
DATA_DIR = Path("data")


def get_daily_data(ticker: str) -> pd.DataFrame:
    """Load daily data from cache or download using yfinance."""
    DATA_DIR.mkdir(exist_ok=True)
    file = DATA_DIR / f"{ticker}_daily.parquet"
    if file.exists():
        df = pd.read_parquet(file)
    else:
        try:
            buf = io.StringIO()
            with redirect_stdout(buf), redirect_stderr(buf):
                df = yf.download(
                    ticker,
                    start=START_DATE,
                    auto_adjust=True,
                    progress=False,
                )
        except Exception as exc:  # pragma: no cover - network failure
            print(f"Failed to download {ticker}: {exc}", file=sys.stderr)
            return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            try:
                df = df.xs(ticker, level=1, axis=1)
            except KeyError:
                df.columns = df.columns.get_level_values(0)
        df.columns.name = None
        df.to_parquet(file, compression="snappy")
    if isinstance(df.columns, pd.MultiIndex):
        try:
            df = df.xs(ticker, level=1, axis=1)
        except KeyError:
            df.columns = df.columns.get_level_values(0)
    df.columns.name = None
    return df


def resample_weekly(daily: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Resample daily OHLCV to weekly bars ending on Friday."""
    file = DATA_DIR / f"{ticker}_weekly.parquet"
    if file.exists():
        return pd.read_parquet(file)
    weekly = daily.resample("W-FRI").agg(
        Open=("Open", "first"),
        High=("High", "max"),
        Low=("Low", "min"),
        Close=("Close", "last"),
        Volume=("Volume", "sum"),
    ).dropna()
    weekly.to_parquet(file, compression="snappy")
    return weekly


def add_indicators(daily: pd.DataFrame, weekly: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Calculate EMA, SMA and ATR indicators."""
    daily = daily.copy()
    weekly = weekly.copy()
    daily["sma200"] = daily["Close"].rolling(200).mean()
    weekly["ema_fast"] = weekly["Close"].ewm(span=10, adjust=False).mean()
    weekly["ema_slow"] = weekly["Close"].ewm(span=30, adjust=False).mean()
    prev_close = weekly["Close"].shift()
    tr = pd.concat(
        [
            weekly["High"] - weekly["Low"],
            (weekly["High"] - prev_close).abs(),
            (weekly["Low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    weekly["atr20"] = tr.rolling(20).mean()
    return daily, weekly


def get_signal(weekly: pd.DataFrame, daily: pd.DataFrame) -> str:
    """Return BUY, SELL or HOLD signal based on EMA crossover and SMA filter."""
    if weekly.empty or daily.empty:
        return "HOLD"
    last_week = weekly.iloc[-1]
    last_close = daily["Close"].iloc[-1]
    sma200 = daily["sma200"].iloc[-1]
    if last_week["ema_fast"] > last_week["ema_slow"] and last_close > sma200:
        return "BUY"
    if last_week["ema_fast"] < last_week["ema_slow"]:
        return "SELL"
    return "HOLD"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="EMA Crossover Signal")
    parser.add_argument("ticker", nargs="?", default="VWCE", help="Ticker symbol (default: VWCE)")
    return parser.parse_args()


def main() -> str:
    args = parse_args()
    daily = get_daily_data(args.ticker)
    if daily.empty:
        return "HOLD"
    weekly = resample_weekly(daily, args.ticker)
    daily, weekly = add_indicators(daily, weekly)
    return get_signal(weekly, daily)


if __name__ == "__main__":
    def _unit_test() -> None:
        """Inline test for expected BUY signal on 2025-06-27."""
        sample_w = pd.DataFrame(
            {"ema_fast": [2], "ema_slow": [1]}, index=[pd.Timestamp("2025-06-27")]
        )
        sample_d = pd.DataFrame(
            {"Close": [10], "sma200": [9]}, index=[pd.Timestamp("2025-06-27")]
        )
        assert get_signal(sample_w, sample_d) == "BUY"
    _unit_test()
    # Expected console output for VWCE on 2025-06-27:
    # BUY
    print(main())
