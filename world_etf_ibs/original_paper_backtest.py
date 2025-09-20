"""
https://arxiv.org/pdf/2306.12434
Idea to cycle in and out of Country-specific ETFs each day for fun and profit.
Using yahooFinance for the data. We're cheap and poor.

Countries and ETFs from the paper:
India   PIN
China   FXI
South Korea EWI
Mexico  EWW
South Africa EZA
Taiwan  EWT
Japan   EWJ
USA IVV
UK  EWU
EU  EZU
Australia   EWA
Singapore   EWS
Canada  EWC
Israel  EIS
Brazil  EWZ
But this feels like there might be selection bias.

IBS is (Close - Low)/(High - Low)

You'll get a long/short Sharpe of like, 3.4 when there's no slippage!?!?

"""

import pandas as pd
import yfinance as yf
import numpy as np
import seaborn as sns
import requests
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
start_date = "2009-01-01"
end_date = "2026-01-01"
slippage = 0#.0001 #0.01%? or 0.05%? slippage??? Need about 13 basis points of slippage to be comparable to SPY's return.
stock_num = 7 # how many top/bottom stocks are we going to check stats for?

# The Sharpe's higher and more consistent at 14 ETFs, so use that.
etf_list = ["IVV", "PIN", "FXI", "EWI", "EWW", "EZA", "EWT", "EWJ", "EWU", "EWA", "EWS", "EWC", "EIS", "EWZ"]
print(etf_list)
ref_etf = etf_list[0]
df = []
for ticker in etf_list:
    temp = yf.download(ticker, start=start_date, end=end_date)
    temp.columns = temp.columns.droplevel(1)
    temp["ticker"] = ticker
    # Return Stuff:
    temp["return"] = (temp["Close"] - temp["Close"].shift(1))/temp["Close"].shift(1)# 1 Day Return
    temp["return_next"] = temp["return"].shift(-1)
    temp["return_previous"] = temp["return"].shift(1)

    temp["ibs"] = (temp["Close"] - temp["Low"]) / (temp["High"] - temp["Low"])
    # Time stuff
    temp["date"] = temp.index.astype(str)
    temp["month"] = temp.index.month
    temp["year"] = temp.index.year
    temp["day"] = temp.index.day
    temp["day_name"] = temp.index.day_name()

    df.append(temp)
    print(ticker, "done")
    print(ticker, "fist trade at:", temp["date"].min(), "latest trade at:", temp["date"].max())

# merge them all together
df = pd.concat(df, axis=0)

# get our reference ETF:
ref = df[df["ticker"] == ref_etf]

df["factor"] = df["ibs"]

# What if we want to make sure we're only trading ETFs with a threshold notional volume?
# We need actual volume to make a trade.
#df = df[df["notional_volume"] > 10000]

# Now rank for each day
df["factor_rank"] = df.groupby("date")["factor"].rank(method="first", ascending=False)
# And ranked the other way, to get Top and Bottom assets by number.
df["factor_rankr"] = df.groupby("date")["factor"].rank(method="first", ascending=True)
# Get the true rank of the next day's return.
df["true_rank"] = df.groupby("date")["return_next"].rank(method="first", ascending=False)
df["true_rankr"] = df.groupby("date")["return_next"].rank(method="first", ascending=True)

# How many assets are in the universe on this day.
df["num_companies"] = df.groupby('date')['ticker'].transform('nunique')

# What about looking at the prior factor_ranks? Just for reference.
window = 21
df["true_rank_prior"] = np.where(df["ticker"] == df["ticker"].shift(1), df["true_rank"].shift(1), np.nan)
df["true_rankr_prior"] = np.where(df["ticker"] == df["ticker"].shift(1), df["true_rankr"].shift(1), np.nan)
df["avg_pred_rank"] = df.groupby('ticker')["factor_rank"].shift(1).transform(lambda x: x.rolling(window, 1).mean())
df["avg_pred_rankr"] = df.groupby('ticker')["factor_rankr"].shift(1).transform(lambda x: x.rolling(window, 1).mean())
df["avg_true_rank"] = df.groupby('ticker')["true_rank_prior"].transform(lambda x: x.rolling(window, 1).mean())
df["avg_true_rankr"] = df.groupby('ticker')["true_rankr_prior"].transform(lambda x: x.rolling(window, 1).mean())

# Sort by date, then Ticker.
df = df.sort_values(by=(["date", "ticker"]), ascending=[True, False])
# What does the true ranking distribution look like?
# Let's see if there's anything weird in this data:
temp = df[df["factor_rankr"] == 1]
#print(temp[["ticker", "date", "return", "return_next", "Open", "High", "Low", "Close", "ibs", "mean_reversion"]].to_string())
# Let's take a look at the "True Rank" Value counts:
# We want factor_rankr == true_rankr, but how often do we get there
print("What is the distribution of Actual Rank for the top-predicted ETFs each day?")
print(temp["true_rankr"].value_counts(sort=True, ascending=False, dropna=True))



# It looks like getting the Top/Bottom 1 ETF is the optimal target.
plt.figure()
plt.xticks(rotation=45)
plt.suptitle(f"Top {stock_num} Ranked ETFs Daily Performance")
plt.title(f"Daily Ranked 'true' performance of stocks")
data_list = []
for i in range(1, stock_num+1):
    temp = df[df["true_rank"] == i]
    plt.plot(pd.to_datetime(temp["date"]), (1 + temp["return_next"]).cumprod(), label=f"Rank-{i}-ETF")
    data_list.append(f"Rank-{i}-ETF")
plt.legend(data_list)
plt.xlabel("Date")
plt.ylabel("Cumulative % Returns")
plt.yscale("log")
plt.show()


# General IBS Distribution:
plt.figure()
plt.suptitle("General IBS Distribution Values")
temp = df[df["ibs"].between(-1,1)]
plt.hist(temp["ibs"], bins = 20, alpha=0.5, label="IBS from ETF Universe")
plt.xlabel("IBS")
plt.ylabel("Count")
plt.legend()
plt.show()




# What is the rough distribution of min and max IBS values?
plt.figure()
plt.suptitle("Min and Max IBS Distribution Values")
temp = df[df["factor_rank"] == 1]
temp = temp[temp["ibs"].between(-1,1)]
plt.hist(temp["ibs"], bins = 20, alpha=0.5, label="IBS Max")
temp = df[df["factor_rankr"] == 1]
temp = temp[temp["ibs"].between(-1,1)]
plt.hist(temp["ibs"], bins = 20, alpha=0.5, label="IBS Min")
plt.xlabel("IBS")
plt.ylabel("Count")
plt.legend()
plt.show()

# Now let's take a look at the performance for this.
plt.figure()
plt.xticks(rotation=45)
plt.suptitle(f"Performance")
plt.title(f"Buy+Hold Performance for ETF Universe")
data_list = []
for ticker in etf_list:
    temp = df[df["ticker"] == ticker]
    plt.plot(pd.to_datetime(temp["date"]),
             (1 + (temp["Close"].shift(-1) - temp["Close"])/temp["Close"]).cumprod(), label=f"{ticker}-ETF")
    data_list.append(f"{ticker}-ETF")
plt.legend(data_list)
plt.xlabel("Date")
plt.ylabel("Cumulative % Returns")
plt.yscale("log")
plt.show()

# We want Top stocks to go up
plt.figure()
plt.xticks(rotation=45)
plt.suptitle(f"Performance")
plt.title(f"Daily top/bottom 1-5 stocks")
data_list = []
for i in range(1, stock_num+1):
    # Top 1-5 By Factor
    temp = df[df["factor_rankr"] == i]
    plt.plot(pd.to_datetime(temp["date"]), (1 + temp["return_next"]-slippage).cumprod(), label=f"ETF-Top-Rank-{i}")
    data_list.append(f"ETF-Top-Rank-{i}")
    # Bottom 1-5 By Factor
    temp = df[df["factor_rank"] == i]
    plt.plot(pd.to_datetime(temp["date"]), (1 + temp["return_next"]+slippage).cumprod(), label=f"ETF-Bottom-Rank-{i}")
    data_list.append(f"ETF-Bottom-Rank-{i}")
plt.plot(pd.to_datetime(ref["date"]),(1 + ref["return_next"]).cumprod(), label=f"{ref_etf} B+H-Index")
# Top minus Bottom
data_list.append(f"{ref_etf} B+H-Index")
plt.legend(data_list)
plt.xlabel("Date")
plt.ylabel("Cumulative % Returns")
plt.yscale("log")
plt.show()

# Take a look at the number of companies available each day:
plt.figure()
plt.xticks(rotation=45)
plt.suptitle(f"Number of ETFs in Available Universe By Day")
temp = df[df["factor_rankr"] == 1]
plt.plot(pd.to_datetime(temp["date"]),temp["num_companies"], label=f"ETFs Available")
# Top minus Bottom
plt.legend(["ETFs Available"])
plt.xlabel("Date")
plt.ylabel("Number")
plt.yscale("linear")
plt.show()



print("\n")
print(f"{ref_etf} Reference:")
temp = ref
print("Averge Monthly Return",temp["return_next"].mean())
print("Percent Positive", np.where(temp["return_next"] > 0, 1, 0).mean())
print("Sharpe", temp["return_next"].mean()/temp["return_next"].std()*np.sqrt(252))
print("Sortino", temp["return_next"].mean()/np.where(temp["return_next"] < 0,temp["return_next"],0).std()*np.sqrt(252))
print("Profit Factor", np.where(temp["return_next"] > 0, temp["return_next"], 0).sum() / (-1 * np.where(temp["return_next"] < 0, temp["return_next"], 0).sum()))
print("Days invested", len(temp))

for i in range(1, stock_num+1):
    print("\n")
    print(f"ETF Daily Low Rank {i}")
    temp = df[df["factor_rankr"] == i]
    print("Averge Daily Return",temp["return_next"].mean()-slippage)
    print("Percent Positive", np.where(temp["return_next"] > 0, 1, 0).mean())
    print("Sharpe", temp["return_next"].mean()/temp["return_next"].std()*np.sqrt(252))
    print("Sortino",temp["return_next"].mean() / np.where(temp["return_next"] < 0, temp["return_next"], 0).std() * np.sqrt(252))
    print("Profit Factor", np.where(temp["return_next"] > 0, temp["return_next"], 0).sum() / (-1*np.where(temp["return_next"] < 0, temp["return_next"], 0).sum()))
    print("Pct Days invested", len(temp)/len(ref)*100)
    #print(f"{len(list(set(temp["ticker"])))} Tickers Used:", list(set(temp["ticker"])))

for i in range(1, stock_num+1):
    print("\n")
    print(f"ETF Daily High Rank {i}")
    temp = df[df["factor_rank"] == i]
    print("Averge Daily Return",temp["return_next"].mean()-slippage)
    print("Percent Positive", np.where(temp["return_next"] > 0, 1, 0).mean())
    print("Sharpe", temp["return_next"].mean()/temp["return_next"].std()*np.sqrt(252))
    print("Sortino",temp["return_next"].mean() / np.where(temp["return_next"] < 0, temp["return_next"], 0).std() * np.sqrt(252))
    print("Profit Factor", np.where(temp["return_next"] > 0, temp["return_next"], 0).sum() / (-1*np.where(temp["return_next"] < 0, temp["return_next"], 0).sum()))
    print("Pct Days invested", len(temp)/len(ref)*100)
    #print(f"{len(list(set(temp["ticker"])))} Tickers Used:", list(set(temp["ticker"])))

