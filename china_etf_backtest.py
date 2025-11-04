
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
yscale = "log"

period_start = "2007-01-01"
period_end = "2026-01-01"
risk_free_rate = 0#.03 / 252

ticker_list = ["FXI", "YXI", #"MCHI", "KWEB", "EMXC",
               "SPY",  "UUP", "TLT", "^VIX", "GLD",  "EEM",
               ]
ticker_list2= ["FXI", #"MCHI", "KWEB", "EMXC",
               "SPY", "UUP", "TLT", "GLD",
               "strat",
               #"YINN", "YANG"
               ]

data = yf.download(ticker_list, start=period_start, end=period_end, auto_adjust=True)[["Close"]]["Close"]
data["weekday"] = data.index.day_name()
data = data[~data["weekday"].isin(["Saturday", "Sunday"])]
for ticker in ticker_list:
    data[f"{ticker}_ret"] = (data[ticker] - data[ticker].shift(1)) / data[ticker].shift(1)
    data[f"{ticker}_prior"] = data[ticker].shift(1)


data["strat_ret"] = risk_free_rate
# Works well:
data["strat_ret"][(data["UUP_ret"].shift(1) <= 0) & (data["SPY_ret"].shift(1) <= 0)] = data["FXI_ret"]
data["strat_ret"][(data["UUP_ret"].shift(1) > 0) & (data["SPY_ret"].shift(1) > 0)] = data["YXI_ret"]
# GLD, SPY, or SLV work on off FXI/YXI days.
#data["strat_ret"][data["strat_ret"] == 0] = data["GLD_ret"]


# NOTE:
# The returns get pretty good after a  > +/-1% move in the relative returns of the USD and SPY
#data["strat_ret"][(data["UUP_ret"].shift(1) - data["SPY_ret"].shift(1)).between(0.01, 1)] = data["FXI_ret"]
#data["strat_ret"][(data["UUP_ret"].shift(1) - data["SPY_ret"].shift(1)).between(-1, -0.01)] = data["YXI_ret"]

#But the returns are terrible (negative over time!) for sub-1% differences.
# So I think there's a theshold change of at least 1% that causes rebalancing.
#data["strat_ret"][(data["UUP_ret"].shift(1) - data["SPY_ret"].shift(1)).between(0, 0.01)] = data["FXI_ret"]
#data["strat_ret"][(data["UUP_ret"].shift(1) - data["SPY_ret"].shift(1)).between(-0.01, 0)] = data["YXI_ret"]

data["strat_used"] = np.where(data["strat_ret"] != risk_free_rate, 1, 0)
#data = data.dropna(how='any')


# now plot cumulative returns
for ticker in ticker_list2:
    data[f"{ticker}_ret_c"] = (1 + data[f"{ticker}_ret"]).cumprod()

# Plot added returns:
for ticker in ticker_list2:
    data[f"{ticker}_ret_a"] = 1 + (data[f"{ticker}_ret"]).cumsum()

plt.figure(dpi=150)
plt.xticks(rotation=45)
plt.suptitle(f"Investigate Compounding Returns for China FXI/YXI Trade")
plt.title(f"Profit over time period") # Get the dates from X to Y as well.
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
plt.suptitle(f"Investigate Arithmatic Returns for China L-S Daily Trade")
plt.title(f"Profit over time period") # Get the dates from X to Y as well.
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


#print("Average Return Difference between EWG and DAX: ", np.mean(abs(data["DAX_ret"] - data["EWG_ret"])))
print("What percent of time invested: ", round(data["strat_used"].mean() * 100, 2), "%")
print("Strategy's Annual Return: ",round((100 * (((1 + data["strat_ret"].mean()) ** 250) - 1)),2), "%")
print("What percent of trades are profitable: ", np.where(data["strat_ret"][data["strat_ret"] != 0] > 0, 1, 0).mean()) # 60%
print("What's the Avg Daily return for the strategy:", round(data["strat_ret"].mean()*100, 2)) # 0.33%
print("What's the Avg Daily return while invested for the strategy:", round(data["strat_ret"][data["strat_ret"] != 0].mean()* 100, 2)) # 0.73%
# Get Sharpe Ratio??
for ticker in ticker_list2:
    print(f"{ticker} Sharpe Ratio: ", round((data[f"{ticker}_ret"].mean() - risk_free_rate) / data[f"{ticker}_ret"].std() * np.sqrt(252),2),
    f" Sortino Ratio: ", round((data[f"{ticker}_ret"].mean() - risk_free_rate) / data[data[f"{ticker}_ret"] < 0][f"{ticker}_ret"].std() * np.sqrt(252),2),
    f" Annual Return: ", round(100 * (((1 + data[f"{ticker}_ret"].mean()) ** 250) - 1),2), "%",
    )

