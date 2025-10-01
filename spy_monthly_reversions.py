"""
A look into Earnings Extrapolation and Predictable Stock Market Returns.

Abstract
The U.S. stock market’s return during the first month of a quarter correlates strongly with
returns in future months, but the correlation is negative if the future month is the first month
of a quarter, and positive if it isn’t. These correlations offset, consistent with the well-known
near-zero unconditional autocorrelation, yet they are pervasive, present across industries
and countries. The pattern accords with a model in which investors extrapolate announced
earnings to predict future earnings, not recognizing that earnings in the first month of a
quarter are discretely less predictable than in prior months. Survey data support the model.

Kinda impressive, tbh.
But how can we use this beyond the asset allocation level???

"""

import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

traded_ticker = "SPY" # ^SPX can go as far back as 1928, but doesn't have a good companion ticker.
other_ticker = "GLD"
risk_free_rate = .03/12.0
start_date = "2003-01-01" # or 1920-01-01
end_date = "2030-01-01"
momentum_length = 12 # or 3, 6, 9, to test different momentum lengths.

data_list = []
for ticker in ["^SPX", "SPY", "TLT", "GLD", "ES=F", "GC=F"]:
    # Let's get Monthly SPX or SPY data:
    data = yf.download(ticker, start=start_date, end=end_date, interval="1d")
    data.columns = data.columns.droplevel(1)
    data = data['Close'].resample('M').ohlc()
    data["return"] = (data["close"] - data["close"].shift(1))/data["close"].shift(1)
    data["prior12MRet"] = (data["close"].shift(1) - data["close"].shift(momentum_length+1))/data["close"].shift(momentum_length+1)
    data = data.add_suffix(f"_{ticker}")
    data_list.append(data)
data = pd.concat(data_list, axis=1)
data["return"] = data[f"return_{traded_ticker}"]
data["prior12MRet"] = data[f"prior12MRet_{traded_ticker}"]
data["date"] = pd.to_datetime(data.index)
data["year"] = data["date"].dt.year
data["month"] = data["date"].dt.month
data["Quarter"] = 1
data.loc[data['month'].isin([4,5,6]), 'Quarter'] = 2
data.loc[data['month'].isin([7,8,9]), 'Quarter'] = 3
data.loc[data['month'].isin([10,11,12]), 'Quarter'] = 4
data["Month_of_Q_Corr"] = np.where(data["month"].isin([1,4,7,10]), -1, 1)
data["prior12M_Q1stM"] = np.where(data["month"].isin([1,4,7,10]), data["return"], 0)
data["prior12M_Q1stM"] = data["prior12M_Q1stM"].shift(1).rolling(12).sum()


# remove so partial momentum factor isn't used.
data = data.drop(data.index[:momentum_length+1])

# Use prior12M_Q1stM or prior12MRet for the momentum using all 12 months, or just the "newsy" months, as defined by the paper.
momentum = "prior12MRet"
#momentum = "prior12M_Q1stM"
# For long/Short
if len(other_ticker) > 1:
    data["Buy/Sell"] = np.where(data["Month_of_Q_Corr"]*data[momentum] > 0, data["return"], data[f"return_{other_ticker}"])
else:
    data["Buy/Sell"] = np.where(data["Month_of_Q_Corr"]*data[momentum] > 0, data["return"], 0)
# for Long/only
data["Buy/Sell1"] = np.where(data["Month_of_Q_Corr"]*data[momentum] > 0, data["return"], 0)
# for short/only
data["Buy/Sell2"] = np.where(data["Month_of_Q_Corr"]*data[momentum] > 0, 0, -data["return"])


data["return_strat"] = data["Buy/Sell"]
data["return_strat_lo"] = data["Buy/Sell1"]
data["return_strat_so"] = data["Buy/Sell2"]

data["return_bm"] = data["return"]

# Get the strategy returns:
data["return_cum"] = (1 + data["Buy/Sell"]).cumprod()
data["return_lo_cum"] = (1 + data["Buy/Sell1"]).cumprod()
data["return_so_cum"] = (1 + data["Buy/Sell2"]).cumprod()
data["return_cum_bm"] = (1 + data["return"]).cumprod()
print(data.head().to_string())
print(data.tail().to_string())

# remove the first 13 points?


for i in ["return_strat", "return_strat_lo", "return_strat_so", "return_bm"]:
    print(
        i,
        f"Sharpe Ratio: ", round((data[i].mean() - risk_free_rate) / data[i].std() * np.sqrt(12), 2),
        f" Sortino Ratio: ", round((data[i].mean() - risk_free_rate) / data[data[i] < 0][i].std() * np.sqrt(12), 2),
        f" Profit Factor: ", round(np.where(data[i] > 0, data[i], 0).sum() / np.where(data[i] < 0,-data[i], 0).sum(),2),
        f" Percent Months Invested: ", round(np.where(data[i] != 0, 1, 0).mean() * 100, 2),
        f" Percent Months Positive: ", round(np.where(data[i] > 0, 1, 0).mean()/np.where(data[i] != 0, 1, 0).mean() * 100, 2),
        f" Avg Period Return: ", round(data[i].mean() * 100, 2),
        f" Std Dev Returns: ", round(data[i].std() * 100, 2),
    )


plt.figure()
plt.xticks(rotation=45)
plt.suptitle(f"Performance of 1-month returns for {traded_ticker}")
plt.title("Growth of $1")
plt.plot(data["date"], data[f"return_cum"])
plt.plot(data["date"], data[f"return_lo_cum"])
plt.plot(data["date"], data[f"return_so_cum"])
plt.plot(data["date"], data[f"return_cum_bm"])
plt.legend([
            f"strat Long {traded_ticker} + {other_ticker}",
            f"strat Long {traded_ticker} only",
            f"strat Short {traded_ticker} only",
            "benchmark",
            ])
plt.xlabel("Date")
plt.ylabel("Cumulative % Returns")
plt.yscale("log")
plt.show()

