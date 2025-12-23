"""
This will take a look at the day before, during, and after a user-provided list of events.
We can then backtest what 1-Day (Close to Close), Intraday (Open to Close), and overnight (Close to Open)
Returns look like for ETFs.

Included currently (as lists of dates):
FOMC Meetings
FOMC Minutes release
Beige Book release
VIX Futures Expiration (VIX OPEX)
SPY Monthly Options Expiration (SPY OPEX)
Triple Witching Day (SPY, ES, SPX OPEX, March, June, September, December)
CPI release
First/Last day of the month
Mid-week (paycheck effect)
ADP National Employment results releases

# upcoming month Example:
# September 2025 Calendar dates? (can be figured out in a day, really)
# FOMC Meetings/Minutes: 2025-09-17
# Beige Book: 2025-09-03
# VIX Futures Expiration 2025-09-17
# SPY Options Expiration 2025-09-19
# Triple Witching 2025-09-19
# CPI 2025-09-11
# First trading day of month 2025-09-02
# ADP National Employment Release 2025-09-04

"""

# LIBRARIES
import pandas as pd
import yfinance as yf
import numpy as np
import plotly.express as px

from scipy import stats

from datetime import datetime
import ssl
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
import warnings
warnings.filterwarnings("ignore")

start_date = "2005-01-01"
today = datetime.today().strftime('%Y-%m-%d')
risk_free_rate = 0.03/252
show_plots = True

from event_dates import fomc_meeting_dates, fomc_minutes_release_dates, beige_book, vix_opex, vix_triple_witching, vix_no_witching, spy_opex, triple_witching, spy_no_witching, adp_nat_emp, cpi_dates, nfp_release, jolts_release



# Let's get weekdays!
all_dates = yf.download("SPY", start=start_date, end=today)
weekday_used = "Friday"
weekday = list(all_dates[pd.to_datetime(all_dates.index).day_name() == weekday_used].index.astype(str).str[:10])
# SPXL does well on Tuesdays 24HR

# Let's get First/Last day of the trading month:
temp = all_dates
temp["month_year"] = pd.to_datetime(temp.index).month.astype(str) + " " + pd.to_datetime(temp.index).year.astype(str)
temp["day"] = pd.to_datetime(temp.index).day
temp["date"] = temp.index
first_day = list(temp.groupby("month_year")["date"].first().astype(str).str[:10])
# First Day of month (close to close)
# During Event - GLD 24HR, EEM 24HR SPY 24HR
last_day = list(temp.groupby("month_year")["date"].last().astype(str).str[:10])
# Last day. Dunno.

# Mid-week? the 15th or after.
mid_week = temp[temp["day"] >= 15]
mid_week = list(mid_week.groupby("month_year")["date"].first().astype(str).str[:10])
# Pre intraday Short Vol (or intraday)
# Post intraday Short Vol (or intraday)


# Create a combination of events, or make each one separate by commenting things in/out.
event_dates = {}
event_dates["fomc_meeting"] = fomc_meeting_dates
event_dates["fomc_minutes_release"] = fomc_minutes_release_dates
event_dates["beige_book"] = beige_book
event_dates["vix_opex"] = vix_opex
event_dates["vix_triple_witching"] = vix_triple_witching
event_dates["vix_no_witching"] = vix_no_witching
event_dates["spy_opex"] = spy_opex
event_dates["triple_witching"] = triple_witching
event_dates["spy_no_witching"] = spy_no_witching
event_dates["weekday"] = weekday
event_dates["first_day"] = first_day # of each month
event_dates["last_day"] = last_day # of each month
event_dates["mid_week"] = mid_week # first trading day on the 15th or after
event_dates["adp_nat_emp"] = adp_nat_emp
event_dates["cpi_dates"] = cpi_dates
event_dates["nfp_release"] = nfp_release
event_dates["jolts_release"] = jolts_release

# Print the Event Days, just so we know what they are
# print(event_dates)

# Get ETF daily data from 2005-01-01 to now:
# tickers = ["VIXY", "UVXY", "SVXY", "SPY", "TLT", "GLD", "EEM"]
tickers = ["VIXY", "UVXY", "SVXY", "SPXL", "SPXU", 'TMF', 'TMV', "GLD", "EEM"]
all_data = []
for ticker in tickers:
    temp_data = yf.download(ticker, start=start_date, end=today)
    temp_data.columns = temp_data.columns.droplevel(1)
    for price in ["Open", "High", "Low", "Close"]:
        temp_data[f"{price}_prior"] = temp_data[price].shift(1)
    # We have 24-hour, 8-hour (intraday) and ~16-hour (overnight)
    # Overnight
    temp_data["Overnight_Return"] = (temp_data["Open"] - temp_data["Close"].shift(1)) / temp_data["Close"].shift(1)
    # Intraday
    temp_data["Intraday_Return"] = (temp_data["Close"] - temp_data["Open"]) / temp_data["Open"]
    # 24 hour:
    temp_data["24_Hour_Return"] = (temp_data["Close"] - temp_data["Close"].shift(1)) / temp_data["Close"].shift(1)
    temp_data = temp_data.add_suffix(f"_{ticker}")
    all_data.append(temp_data)

all_data = pd.concat(all_data, axis = 1)
all_data["date"] = all_data.index.strftime("%Y-%m-%d")
all_data["prior_trading_day"] = all_data["date"].shift(1)
all_data["next_trading_day"] = all_data["date"].shift(-1)
all_data["weekday"] = all_data.index.day_name()

# breakpoint()
# all_data["pre_event_day"] = np.where(all_data["next_trading_day"].isin(event_dates), 1, 0)
# all_data["event_day"] = np.where(all_data["date"].isin(event_dates), 1, 0)
# all_data["post_event_day"] = np.where(all_data["prior_trading_day"].isin(event_dates), 1, 0)
# all_data["all_days"] = (all_data.pre_event_day == 1) | (all_data.event_day == 1) | (all_data.post_event_day == 1)

# # Now, let's limit to Event Pre/During/Post days
# mask = (all_data["pre_event_day"] == 1) | (all_data["event_day"] == 1) | (all_data["post_event_day"] == 1)
# event_data = all_data.loc[mask].copy()


# What if we ignore any days where: VIX > VIX3M, (Would need to add ^VIX and ^VIX3M to the tickers list.)
# event_data['VIX_in_Backwardation'] = event_data["Close_prior_^VIX"] < event_data["Close_prior_^VIX3M"]

# Let's look at the return data for each:
# Let's Take a look at the Metrics:

results = []
for event, dates in event_dates.items():
    all_data["pre_event_day"] = np.where(all_data["next_trading_day"].isin(dates), 1, 0)
    all_data["event_day"] = np.where(all_data["date"].isin(dates), 1, 0)
    all_data["post_event_day"] = np.where(all_data["prior_trading_day"].isin(dates), 1, 0)
    all_data["all_days"] = (all_data.pre_event_day == 1) | (all_data.event_day == 1) | (all_data.post_event_day == 1)

    # Now, let's limit to Event Pre/During/Post days
    mask = (all_data["pre_event_day"] == 1) | (all_data["event_day"] == 1) | (all_data["post_event_day"] == 1)
    event_data = all_data.loc[mask].copy()

    for day_type in ['pre_event_day', 'event_day', 'post_event_day', 'all_days']:
        _data = event_data.loc[event_data[day_type] == 1].dropna()
        for return_type in ['Overnight_Return', 'Intraday_Return', '24_Hour_Return']:
            for ticker in tickers:
                ret = _data[f"{return_type}_{ticker}"]
                out = {}
                out['start_date'] = _data.index[0].strftime("%Y-%m-%d")
                out['event'] = event
                out['day_type'] = day_type
                out['retrun_type'] = return_type
                out['ticker'] = ticker
                out['Total_return %'] = ((1+ret).cumprod() - 1)[-1] *100
                out['Pct Profitable'] = np.where(ret > 0, 1, 0).mean() * 100
                out['Avg % ret'] = ret.mean() * 100
                out['sharpe'] = ret.mean() / ret.std() * np.sqrt(252)
                out['sortino'] = ret.mean() / ret.loc[ret < 0].std() * np.sqrt(252)
                tt = stats.ttest_1samp(ret, popmean=0.0)
                out['p_value'] = tt.pvalue
                out['df'] = tt.df
                if np.isnan(tt.pvalue): breakpoint()
                # out['profit factor']

                results.append(out)

results = pd.DataFrame(results)

# event_max_sharpe = results.groupby(['event', 'day_type']).sharpe.idxmax().values
# results.iloc[event_max_sharpe].sort_values('sharpe').tail(50)

event_min_pvalue = results.loc[results.day_type != 'all_days'].groupby(['event', 'day_type']).p_value.idxmin().values
# results.iloc[event_min_pvalue].sort_values('sharpe').tail(50)

event_max_sharpe = results.loc[results.day_type != 'all_days'].groupby(['event', 'day_type']).sharpe.idxmax().values
# results.iloc[event_max_sharpe].sort_values('sharpe').tail(50)

# event_max_sharpe = results.loc[(results.day_type != 'all_days') & (results.sharpe > 0) & (results.p_value < 0.1)].groupby(['event', 'day_type']).sharpe.idxmax().values

use_trades = results.iloc[event_max_sharpe]

print(use_trades.to_string())

returns = []
for row, trade in use_trades.iterrows():
    if (trade.event == 'weekday') & (trade.day_type != 'post_event_day'):
        continue
    dates = event_dates.get(trade.event)
    if trade.day_type == 'pre_event_day':
        mask = all_data.next_trading_day.isin(dates)
    elif trade.day_type == 'post_event_day':
        mask = all_data.prior_trading_day.isin(dates)
    else:
        mask = all_data.date.isin(dates)
    # mask = mask & (all_data[trade.day_type] == 1)
    _ = ret = all_data.loc[mask, f"{trade.retrun_type}_{trade.ticker}"].dropna()
    _ = _.loc[_.index > trade.start_date]
    returns.append(_)

returns_df = pd.concat(returns).sort_index().fillna(0).to_frame('ret').groupby('Date').ret.mean().to_frame('ret')
returns_df['cpnl'] = 10000 * (returns_df.ret + 1).cumprod()
returns_df['date'] = returns_df.index
px.line(returns_df, x='date', y='cpnl', title='CPNL', log_y=True).show()

def summary_stats(df: pd.DataFrame, equity_col: str = 'equity'):
    """Summary statistics"""
    ret = df[equity_col].pct_change()
    sr = ret.mean() / ret.std() * np.sqrt(252)
    st = ret.mean() / ret[ret < 0].std() * np.sqrt(252)
    total_days = (df.date.iloc[-1] - df.date.iloc[0]).days
    years = (total_days / 365)
    cagr = (df[equity_col].iloc[-1] / df[equity_col].iloc[0]) ** (1/years) - 1
    max_drawdown = (df[equity_col] / df[equity_col].cummax() - 1).min()
    print(f"         Total days : {total_days}, {years:.2f} years")
    print(f" Total trading days : {len(df)}")
    print(f"       Sharpe ratio : {sr:.2f}")
    print(f'      Sortino ratio : {st:.2f}')
    print(f"               CAGR : {cagr:.2%}")
    print(f"         Volatility : {ret.std() * np.sqrt(252):.2%}")
    print(f"Downside Volatility : {ret[ret < 0].std() * np.sqrt(252):.2%}")
    print(f"       Total return : {(df[equity_col].iloc[-1] / df[equity_col].iloc[0] - 1):.2%}")
    print(f"     Initial equity : ${df[equity_col].iloc[0]:.2f}")
    print(f"       Final equity : ${df[equity_col].iloc[-1]:.2f}")
    print(f"       Max drawdown : {max_drawdown:.2%}")

summary_stats(returns_df, 'cpnl')


