"""IBS multi-ticker backtest and signal generator.

Installation:
    pip install yfinance pandas numpy matplotlib pyarrow python-dateutil --upgrade

Example:
    python ibs_multi.py --tickers "SPY,QQQ" --ibs_buy 0.25 --ibs_sell 0.75
"""

from __future__ import annotations

import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import yfinance as yf
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt

DATA_DIR = Path("data")
PLOT_DIR = Path("plots")
RESULT_DIR = Path("results")

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def download_historical_data(
    ticker: str, start: str, end: str
) -> Optional[pd.DataFrame]:
    """Download daily OHLC data using yfinance with Parquet caching."""
    DATA_DIR.mkdir(exist_ok=True)
    file = DATA_DIR / f"{ticker}.parquet"
    end_dt = pd.to_datetime(end).date()
    today = datetime.today().date()
    if file.exists() and end_dt <= today:
        logging.info("Loading %s from cache", ticker)
        return pd.read_parquet(file)
    try:
        logging.info("Downloading %s", ticker)
        df = yf.download(ticker, start=start, end=end, progress=False)
    except Exception as exc:  # pragma: no cover - network issues
        logging.error("Failed to download %s: %s", ticker, exc)
        return None
    if df.empty:
        logging.error("No data for %s", ticker)
        return None
    df = df[["Open", "High", "Low", "Close"]]
    df.to_parquet(file, compression="snappy")
    return df


def calculate_ibs(data: pd.DataFrame) -> pd.Series:
    """Compute Internal Bar Strength (IBS)."""
    data = data.copy()
    data["IBS"] = np.where(
        (data["High"] - data["Low"]) != 0,
        (data["Close"] - data["Low"]) / (data["High"] - data["Low"]),
        0,
    )
    return data["IBS"]


def backtest_strategy(
    data: pd.DataFrame, ibs_buy: float, ibs_sell: float
) -> pd.DataFrame:
    """Apply IBS thresholds and compute strategy performance."""
    df = data.copy()
    df["Buy_Signal"] = (df["IBS"] <= ibs_buy).astype(int)
    df["Sell_Signal"] = (df["IBS"] >= ibs_sell).astype(int)
    df["Market_Return"] = df["Close"].pct_change()
    signals = pd.Series(np.nan, index=df.index)
    signals[df["IBS"] <= ibs_buy] = 1
    signals[df["IBS"] >= ibs_sell] = 0
    df["position"] = signals.shift(1).ffill().fillna(0).astype(int)
    df["Strategy_Return"] = df["position"].shift(1) * df["Market_Return"]
    df["Cumulative_Market_Return"] = (1 + df["Market_Return"]).cumprod() - 1
    df["Cumulative_Strategy_Return"] = (1 + df["Strategy_Return"]).cumprod() - 1
    return df


def plot_strategy_performance(df: pd.DataFrame, ticker: str, show: bool) -> None:
    """Save side-by-side plots of cumulative returns."""
    PLOT_DIR.mkdir(exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].plot(df.index, df["Cumulative_Market_Return"], label="Market")
    axes[0].set_title(f"{ticker} Market Return")
    axes[1].plot(df.index, df["Cumulative_Strategy_Return"], label="Strategy", color="orange")
    axes[1].set_title(f"{ticker} Strategy Return")
    for ax in axes:
        ax.set_xlabel("Date")
        ax.set_ylabel("Cumulative Return")
        ax.legend()
    fig.tight_layout()
    outfile = PLOT_DIR / f"{ticker}_ibs_perf.png"
    fig.savefig(outfile)
    logging.info("Saved plot to %s", outfile)
    if show:
        plt.show()
    plt.close(fig)


def summarize(df: pd.DataFrame) -> tuple[float, float, int, int]:
    """Return summary stats from backtest DataFrame."""
    total_strat = df["Cumulative_Strategy_Return"].iloc[-1] * 100
    total_market = df["Cumulative_Market_Return"].iloc[-1] * 100
    buys = int(df["Buy_Signal"].sum())
    sells = int(df["Sell_Signal"].sum())
    return total_strat, total_market, buys, sells


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="IBS multi-ticker backtest")
    parser.add_argument(
        "--tickers",
        default="SPY,QQQ,IWM,EFA,VNQ",
        help="Comma-separated tickers",
    )
    parser.add_argument("--ibs_buy", type=float, default=0.20, help="IBS buy threshold")
    parser.add_argument("--ibs_sell", type=float, default=0.80, help="IBS sell threshold")
    parser.add_argument("--start", type=str, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", type=str, help="End date YYYY-MM-DD")
    parser.add_argument(
        "--no-plot", dest="plot", action="store_false", help="Disable plots"
    )
    parser.set_defaults(plot=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    end = args.end or datetime.today().strftime("%Y-%m-%d")
    start = args.start or (datetime.today() - relativedelta(years=10)).strftime("%Y-%m-%d")
    tickers = [t.strip().upper() for t in args.tickers.split(",") if t.strip()]

    summaries: list[dict[str, object]] = []
    for ticker in tickers:
        df = download_historical_data(ticker, start, end)
        if df is None:
            continue
        df["IBS"] = calculate_ibs(df)
        df = backtest_strategy(df, args.ibs_buy, args.ibs_sell)
        latest_ibs = df["IBS"].iloc[-1]
        if latest_ibs <= args.ibs_buy:
            signal = "BUY"
        elif latest_ibs >= args.ibs_sell:
            signal = "SELL"
        else:
            signal = "HOLD"
        print(f"{ticker}  latest IBS={latest_ibs:.2f}  ⇒  {signal}")
        if args.plot:
            plot_strategy_performance(df, ticker, show=False)
        total_strat, total_market, buys, sells = summarize(df)
        summaries.append(
            {
                "ticker": ticker,
                "cumulative_strategy_return": total_strat,
                "cumulative_market_return": total_market,
                "buy_signals": buys,
                "sell_signals": sells,
            }
        )

    if summaries:
        summary_df = pd.DataFrame(summaries)
        summary_df = summary_df.round(
            {"cumulative_strategy_return": 2, "cumulative_market_return": 2}
        )
        print("\n", summary_df.to_string(index=False))
        RESULT_DIR.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file = RESULT_DIR / f"ibs_summary_{timestamp}.csv"
        summary_df.to_csv(file, index=False)
        logging.info("Saved summary to %s", file)


if __name__ == "__main__":
    main()
