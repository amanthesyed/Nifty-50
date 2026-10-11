# NIFTY 50 Market Analysis

A small Python market-data project exploring the Indian NIFTY 50 index and how a selected NSE-listed stock moves relative to it. It focuses on readable analysis and explicit assumptions—not automated trading or stock recommendations.

## Scripts

### `nifty_index_analysis.py`

Downloads Yahoo Finance's `^NSEI` index series and plots:
- Index level with a 20-trading-day moving average and Bollinger range
- Distribution of daily returns
- 20-day rolling volatility, annualised using 252 trading days

It also prints the coverage period, latest available close, mean daily return, and annualised volatility estimate.

### `compare_stock_to_nifty.py`

Compares a selected listed stock against `^NSEI`:
- Relative performance rebased to 100 on the first shared trading day
- Rolling annualised volatility
- Daily-return scatter plot and correlation
- Augmented Dickey–Fuller test statistics for each daily-return series

## Run locally

Requires Python 3.10 or newer.

~~~bash
git clone https://github.com/amanthesyed/Nifty-50.git
cd Nifty-50
python -m venv .venv
~~~

Activate the virtual environment, then install the dependencies:

~~~bash
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
python nifty_index_analysis.py
python compare_stock_to_nifty.py --ticker TCS.NS --start-date 2022-01-01
~~~

The comparison script defaults to `RELIANCE.NS`. Use Yahoo Finance ticker formats such as `TCS.NS`, `INFY.NS`, or `HDFCBANK.NS` for NSE-listed stocks.

## Data and interpretation

- Both scripts use Yahoo Finance data through `yfinance`; availability, adjusted prices, and historical coverage depend on that provider.
- The index analysis uses `^NSEI` directly. The earlier prototype labelled a basket of international individual-stock tickers as NIFTY 50; that was not a valid NIFTY 50 constituent list and has been replaced.
- Rolling volatility is the standard deviation of daily returns multiplied by the square root of 252. It is an annualised historical estimate, not a forecast.
- Bollinger bands are calculated from the index level's 20-day moving average and standard deviation.
- ADF results depend on the selected date range and test assumptions; a p-value is not a standalone trading signal.
- This repository is an educational analysis project, not financial advice.

## Dependencies

Python · pandas · yfinance · matplotlib · statsmodels
