"""Explore the NIFTY 50 index: trend, return distribution, and rolling volatility.

Market data is retrieved from Yahoo Finance through yfinance. This is an
exploratory analysis tool, not a trading signal or investment recommendation.
"""
from datetime import date
from math import sqrt

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf


INDEX_TICKER = "^NSEI"
DEFAULT_START_DATE = "2019-01-01"


def fetch_close(ticker: str, start_date: str) -> pd.Series:
    """Download adjusted close prices, handling yfinance column variations."""
    data = yf.download(
        ticker,
        start=start_date,
        end=date.today().isoformat(),
        auto_adjust=True,
        progress=False,
        threads=False,
    )
    if data.empty:
        raise RuntimeError(
            f"No market data returned for {ticker!r}. Check the ticker, "
            "date range, and Yahoo Finance availability."
        )

    close = data["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    return close.dropna().rename("NIFTY 50")


def main() -> None:
    close = fetch_close(INDEX_TICKER, DEFAULT_START_DATE)
    returns = close.pct_change().dropna()
    moving_average = close.rolling(window=20).mean()
    rolling_std = close.rolling(window=20).std()
    upper_band = moving_average + 2 * rolling_std
    lower_band = moving_average - 2 * rolling_std
    annualised_volatility = returns.rolling(window=20).std() * sqrt(252)

    print(f"Index: {INDEX_TICKER} (NIFTY 50)")
    print(f"Observations: {len(close):,}")
    print(f"Period: {close.index.min().date()} to {close.index.max().date()}")
    print(f"Latest close: {close.iloc[-1]:,.2f}")
    print(f"Mean daily return: {returns.mean():.4%}")
    print(f"Annualised volatility (daily-return estimate): "
          f"{returns.std() * sqrt(252):.2%}")

    fig, axes = plt.subplots(3, 1, figsize=(13, 12), constrained_layout=True)

    axes[0].plot(close.index, close, label="NIFTY 50", linewidth=1.5)
    axes[0].plot(moving_average.index, moving_average, label="20-day SMA", linewidth=1)
    axes[0].fill_between(
        close.index,
        lower_band,
        upper_band,
        alpha=0.15,
        label="20-day Bollinger band (±2 standard deviations)",
    )
    axes[0].set_title("NIFTY 50 — price trend and rolling range")
    axes[0].set_ylabel("Index level")
    axes[0].legend()
    axes[0].grid(alpha=0.25)

    axes[1].hist(returns, bins=50, edgecolor="white")
    axes[1].set_title("Distribution of daily returns")
    axes[1].set_xlabel("Daily return")
    axes[1].set_ylabel("Trading days")
    axes[1].grid(alpha=0.2)

    axes[2].plot(
        annualised_volatility.index,
        annualised_volatility * 100,
        label="20-day rolling, annualised",
    )
    axes[2].set_title("Rolling realised volatility")
    axes[2].set_ylabel("Volatility (%)")
    axes[2].legend()
    axes[2].grid(alpha=0.25)

    plt.show()


if __name__ == "__main__":
    main()
