"""Compare a listed Indian stock with the NIFTY 50 index.

Example:
    python compare_stock_to_nifty.py --ticker TCS.NS --start-date 2022-01-01

This is an exploratory market-data analysis, not investment advice.
"""
import argparse
from datetime import date
from math import sqrt

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
from statsmodels.tsa.stattools import adfuller


INDEX_TICKER = "^NSEI"


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
    return close.dropna().rename(ticker)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare a stock's returns and volatility with the NIFTY 50."
    )
    parser.add_argument(
        "--ticker",
        default="RELIANCE.NS",
        help="Yahoo Finance ticker for the stock (default: RELIANCE.NS)",
    )
    parser.add_argument(
        "--start-date",
        default="2022-01-01",
        help="Inclusive start date in YYYY-MM-DD format (default: 2022-01-01)",
    )
    args = parser.parse_args()

    stock_ticker = args.ticker.strip().upper()
    if not stock_ticker:
        parser.error("--ticker cannot be empty")

    prices = pd.concat(
        [
            fetch_close(INDEX_TICKER, args.start_date),
            fetch_close(stock_ticker, args.start_date),
        ],
        axis=1,
        join="inner",
    ).dropna()

    if len(prices) < 30:
        raise RuntimeError(
            "Fewer than 30 overlapping trading observations were returned; "
            "choose an earlier start date or another ticker."
        )

    returns = prices.pct_change().dropna()
    rolling_volatility = returns.rolling(window=20).std() * sqrt(252)
    indexed_prices = prices / prices.iloc[0] * 100

    print(f"Benchmark: {INDEX_TICKER} (NIFTY 50)")
    print(f"Comparison: {stock_ticker}")
    print(f"Overlapping observations: {len(prices):,}")
    print(f"Period: {prices.index.min().date()} to {prices.index.max().date()}")
    print(f"Daily-return correlation: "
          f"{returns[INDEX_TICKER].corr(returns[stock_ticker]):.3f}")

    for ticker in (INDEX_TICKER, stock_ticker):
        series = returns[ticker].dropna()
        adf_stat, p_value, *_ = adfuller(series)
        print(
            f"{ticker}: annualised volatility={series.std() * sqrt(252):.2%}; "
            f"ADF statistic={adf_stat:.3f}; p-value={p_value:.4f}"
        )

    fig, axes = plt.subplots(3, 1, figsize=(13, 12), constrained_layout=True)

    indexed_prices.plot(ax=axes[0], linewidth=1.4)
    axes[0].set_title("Relative price performance (first shared close = 100)")
    axes[0].set_ylabel("Indexed price")
    axes[0].grid(alpha=0.25)

    (rolling_volatility * 100).plot(ax=axes[1], linewidth=1.2)
    axes[1].set_title("20-day rolling annualised volatility")
    axes[1].set_ylabel("Volatility (%)")
    axes[1].grid(alpha=0.25)

    axes[2].scatter(
        returns[INDEX_TICKER],
        returns[stock_ticker],
        alpha=0.35,
        s=18,
    )
    axes[2].set_title("Daily return relationship")
    axes[2].set_xlabel("NIFTY 50 daily return")
    axes[2].set_ylabel(f"{stock_ticker} daily return")
    axes[2].grid(alpha=0.25)

    plt.show()


if __name__ == "__main__":
    main()
