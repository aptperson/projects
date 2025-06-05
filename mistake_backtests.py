# This file covers issues trading /GC+GLD and DAX+EWG
# Geometric returns: you're investing 100% of the portfolio into the positions
# Simple (Arithmatic) returns: you're investing a set amount of money each time gains/losses aren't reinvested.

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
yscale = "log"


"""
Covering the /GC GLD trading backtests
"""

period_start = "2000-01-01"
period_end = "2026-01-01"
risk_free_rate = 0.03 / 252

ticker_list = ["GLD", "GC=F", "SPY", "TLT", "^VIX", "^VIX3M"]
ticker_list2= ["GLD", "GC=F", "SPY", "TLT", "strat_ls", "strat_long_only"]

data = yf.download(ticker_list, start=period_start, end=period_end, auto_adjust=True)[["Close"]]["Close"]
data["weekday"] = data.index.day_name()
data = data[~data["weekday"].isin(["Saturday", "Sunday"])]
for ticker in ticker_list:
    data[f"{ticker}_ret"] = (data[ticker] - data[ticker].shift(1)) / data[ticker].shift(1)
    data[f"{ticker}_prior"] = data[ticker].shift(1)

# Long/Short Gold Futures based on relative return to GLD
data["strat_ls_ret"] = risk_free_rate
data["strat_ls_ret"][(data["GLD_ret"].shift(1) > data["GC=F_ret"].shift(1))
    ] = data["GC=F_ret"]
data["strat_ls_ret"][(data["GLD_ret"].shift(1) <= data["GC=F_ret"].shift(1))
    ] = -data["GC=F_ret"]

# Gold Futures Long Only
data["strat_long_only_ret"] = risk_free_rate
data["strat_long_only_ret"][(data["GLD_ret"].shift(1) > data["GC=F_ret"].shift(1))
    ] = data["GC=F_ret"]



data["strat_used"] = np.where(data["strat_long_only_ret"] != risk_free_rate, 1, 0)
data = data.dropna(how='any')


# now plot cumulative returns
for ticker in ticker_list2:
    data[f"{ticker}_ret_c"] = (1 + data[f"{ticker}_ret"]).cumprod()

# Plot added returns:
for ticker in ticker_list2:
    data[f"{ticker}_ret_a"] = 1 + (data[f"{ticker}_ret"]).cumsum()

plt.figure(dpi=150)
plt.xticks(rotation=45)
plt.suptitle(f"Investigate Compounding Returns for /GC L-S Daily Trade")
plt.title(f"Profit over time period")
legend_list = []
for ticker in ticker_list2:
    temp2 =f"{ticker} Return"
    plt.plot(data.index, data[f"{ticker}_ret_c"], label=temp2)
    legend_list.append(temp2)
plt.legend(legend_list)
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
plt.tight_layout()
plt.yscale(yscale)
plt.show()


plt.figure(dpi=150)
plt.xticks(rotation=45)
plt.suptitle(f"Investigate Simple Returns for /GC L-S Daily Trade")
plt.title(f"Profit over time period")
legend_list = []
for ticker in ticker_list2:
    temp2 =f"{ticker} Return"
    plt.plot(data.index, data[f"{ticker}_ret_a"], label=temp2)
    legend_list.append(temp2)
plt.legend(legend_list)
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
plt.tight_layout()
plt.yscale(yscale)
plt.show()


print("What percent of time invested in Long-Only /GC: ", round(data["strat_used"].mean() * 100, 2), "%")
print("Strategy's Annual Return: ",round((100 * (((1 + data["strat_ls_ret"].mean()) ** 250) - 1)),2), "%")
print("What percent of trades are profitable: ", np.where(data["strat_ls_ret"][data["strat_ls_ret"] != 0] > 0, 1, 0).mean()) # 60%
print("What's the Avg Daily return for the strategy:", round(data["strat_ls_ret"].mean()*100, 2)) # 0.33%
print("What's the Avg Daily return while invested for the strategy:", round(data["strat_ls_ret"][data["strat_ls_ret"] != 0].mean()* 100, 2)) # 0.73%
# Get Sharpe, Sortino, and Annual Return
for ticker in ticker_list2:
    print(f"{ticker} Sharpe Ratio: ", round((data[f"{ticker}_ret"].mean() - risk_free_rate) / data[f"{ticker}_ret"].std() * np.sqrt(252),2),
    f" Sortino Ratio: ", round((data[f"{ticker}_ret"].mean() - risk_free_rate) / data[data[f"{ticker}_ret"] < 0][f"{ticker}_ret"].std() * np.sqrt(252),2),
    f" Annual Return: ", round(100 * (((1 + data[f"{ticker}_ret"].mean()) ** 250) - 1),2), "%",
    )




"""
Covering the DAX+EWG trading backtests.
"""
period_start = "2000-01-01"
period_end = "2026-01-01"
risk_free_rate = 0.03 / 252

ticker_list = ["DAX", "EWG", "SPY", "TLT", "^VIX", "^VIX3M", "GLD",]
ticker_list2= ["DAX", "EWG", "SPY", "TLT", "GLD", "strat", "strat_ls", "strat_long_only"]

data = yf.download(ticker_list, start=period_start, end=period_end, auto_adjust=True)[["Close"]]["Close"]
data["weekday"] = data.index.day_name()
data = data[~data["weekday"].isin(["Saturday", "Sunday"])]
for ticker in ticker_list:
    data[f"{ticker}_ret"] = (data[ticker] - data[ticker].shift(1)) / data[ticker].shift(1)
    data[f"{ticker}_prior"] = data[ticker].shift(1)


data["strat_ret"] = risk_free_rate
data["strat_ret"][(data["DAX_ret"].shift(1) < data["EWG_ret"].shift(1))
    ] = data["DAX_ret"]
data["strat_ret"][(data["DAX_ret"].shift(1) >= data["EWG_ret"].shift(1))
    ] = -data["DAX_ret"]


data["strat_ls_ret"] = risk_free_rate
data["strat_ls_ret"][(data["DAX_ret"].shift(1) < data["EWG_ret"].shift(1))
    ] = data["DAX_ret"] - data["EWG_ret"]
data["strat_ls_ret"][(data["DAX_ret"].shift(1) >= data["EWG_ret"].shift(1))
    ] = -data["DAX_ret"] + data["EWG_ret"]


data["strat_long_only_ret"] = risk_free_rate
data["strat_long_only_ret"][(data["DAX_ret"].shift(1) < data["EWG_ret"].shift(1))
    ] = data["DAX_ret"]


data["strat_used"] = np.where(data["strat_ret"] != risk_free_rate, 1, 0)
data = data.dropna(how='any')


# now plot cumulative returns
for ticker in ticker_list2:
    data[f"{ticker}_ret_c"] = (1 + data[f"{ticker}_ret"]).cumprod()

# Plot added returns:
for ticker in ticker_list2:
    data[f"{ticker}_ret_a"] = 1 + (data[f"{ticker}_ret"]).cumsum()

plt.figure(dpi=150)
plt.xticks(rotation=45)
plt.suptitle(f"Investigate Compounding Returns for DAX/EWG L-S Daily Trade")
plt.title(f"Profit over time period")
legend_list = []
for ticker in ticker_list2:
    temp2 =f"{ticker} Return"
    plt.plot(data.index, data[f"{ticker}_ret_c"], label=temp2)
    legend_list.append(temp2)
plt.legend(legend_list)
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
plt.tight_layout()
plt.yscale(yscale)
plt.show()


plt.figure(dpi=150)
plt.xticks(rotation=45)
plt.suptitle(f"Investigate Simple Returns for DAX/EWG L-S Daily Trade")
plt.title(f"Profit over time period")
legend_list = []
for ticker in ticker_list2:
    temp2 =f"{ticker} Return"
    plt.plot(data.index, data[f"{ticker}_ret_a"], label=temp2)
    legend_list.append(temp2)
plt.legend(legend_list)
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
plt.tight_layout()
plt.yscale(yscale)
plt.show()


print("Average Return Difference between EWG and DAX: ", np.mean(abs(data["DAX_ret"] - data["EWG_ret"])))
print("What percent of time invested: ", round(data["strat_used"].mean() * 100, 2), "%")
print("Strategy's Annual Return: ",round((100 * (((1 + data["strat_ret"].mean()) ** 250) - 1)),2), "%")
print("What percent of trades are profitable: ", np.where(data["strat_ret"][data["strat_ret"] != 0] > 0, 1, 0).mean())
print("What's the Avg Daily return for the strategy:", round(data["strat_ret"].mean()*100, 2))
print("What's the Avg Daily return while invested for the strategy:", round(data["strat_ret"][data["strat_ret"] != 0].mean()* 100, 2))
# Get Sharpe, Sortino, and Annual return
for ticker in ticker_list2:
    print(f"{ticker} Sharpe Ratio: ", round((data[f"{ticker}_ret"].mean() - risk_free_rate) / data[f"{ticker}_ret"].std() * np.sqrt(252),2),
    f" Sortino Ratio: ", round((data[f"{ticker}_ret"].mean() - risk_free_rate) / data[data[f"{ticker}_ret"] < 0][f"{ticker}_ret"].std() * np.sqrt(252),2),
    f" Annual Return: ", round(100 * (((1 + data[f"{ticker}_ret"].mean()) ** 250) - 1),2), "%",
    )
