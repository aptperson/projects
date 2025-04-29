from polygon import RESTClient
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

# Let's make a historical chart of VIX and VIX1D
# VIX
vix = yf.download("^VIX", start="2000-01-01", end="2030-01-01")
vix.columns = vix.columns.droplevel(1)
# VIX1D
vix1d = yf.download("^VIX1D", start="2000-01-01", end="2030-01-01")
vix1d.columns = vix1d.columns.droplevel(1)


plt.figure(dpi=150)
plt.xticks(rotation=45)
plt.suptitle(f"VIX Index Levels")
plt.plot(vix.index, vix["Close"])
plt.show()

plt.figure(dpi=150)
plt.xticks(rotation=45)
plt.suptitle(f"VIX1D Index Levels")
plt.plot(vix1d.index, vix1d["Close"])
plt.show()

# We see these Volatility Indices tend spike and revert, over and over.
yscale = "linear"
period_start = "2023-04-22"
period_end = "2025-04-28"
risk_free_rate = 0.03 / 252
vix_lower_bound = 10
vix_upper_bound = 15
portfolio_start = 1
use = "polygon" # or "yfinance
client = RESTClient("POLYGON API KEY HERE")
# want the hour 15, 50-minute timeframe.
def get_daily_near_closing_value(ticker=None, hour=15, minute=50):
    aggs = []
    for a in client.list_aggs(
            ticker,
            5,
            "minute",
            "2023-04-22",
            "2025-04-28",
            sort="asc",
            limit=50000,
    ):
        aggs.append(a)

    dataframe = pd.DataFrame(aggs)[["close", "timestamp"]]
    dataframe["date"] = pd.to_datetime(dataframe["timestamp"], unit='ms', utc=True).dt.tz_convert('US/Eastern')
    dataframe["date_small"] = dataframe["date"].dt.date
    dataframe["minute"] = dataframe["date"].dt.minute
    dataframe["hour"] = dataframe["date"].dt.hour
    dataframe = dataframe[(dataframe["hour"] == hour) & (dataframe["minute"] == minute)]
    dataframe = dataframe.set_index('date_small')
    return dataframe[["close"]].add_suffix(f"_{ticker}")


ticker_list = ["SPY", "^VIX", "^VIX1D", "^VIX3M", "SVXY", "VIXY", "SVIX"]
ticker_list2 = ticker_list + ["strat"]
data = None
if use == "yfinance":
    data = yf.download(ticker_list, start=period_start, end=period_end)[["Close"]]["Close"]
elif use == "polygon":
    #ticker_list = ["SPY", "I:VIX", "I:VIX1D", "I:VIX3M", "SVXY", "VIXY", "SVIX"]
    spy = get_daily_near_closing_value(ticker="SPY")
    vixy = get_daily_near_closing_value(ticker="VIXY")
    svxy = get_daily_near_closing_value(ticker="SVXY")
    svix = get_daily_near_closing_value(ticker="SVIX")
    vix = get_daily_near_closing_value(ticker="I:VIX")
    vix3m = get_daily_near_closing_value(ticker="I:VIX3M")
    vix1d = get_daily_near_closing_value(ticker="I:VIX1D")
    polygon_data = pd.concat([spy, vixy, svxy, svix, vix, vix3m, vix1d], axis=1)
    data = polygon_data
    data = data.rename(columns={"close_SPY": "SPY",
                                "close_I:VIX": "^VIX",
                                "close_I:VIX1D": "^VIX1D",
                                "close_I:VIX3M": "^VIX3M",
                                "close_SVXY": "SVXY",
                                "close_VIXY": "VIXY",
                                "close_SVIX": "SVIX"})
else:
    print("Error")

#print(data.head().to_string())


data["strat_ret"] = 0 # general stategy
data["strat_vixy_ret"] = 0 # strategy's VIXY component
data["strat_svxy_ret"] = 0 # strategy's SVXY component
data["strat_svix_ret"] = 0 # strategy's SVIX component, if taking more risk
data["strat_vix>vix3m_ret"] = 0 # strategy when VIX is in Backwardation
data["strat_vix<vix3m_ret"] = 0 # strategy when VIX is in Contango

for ticker in ticker_list:
    data[f"{ticker}_ret"] = (data[ticker] - data[ticker].shift(1)) / data[ticker].shift(1)
    data[f"{ticker}_prior"] = data[ticker].shift(1)

# VIXY
data["strat_ret"][(data["^VIX1D_prior"] < vix_lower_bound)] = data["VIXY_ret"]
data["strat_vixy_ret"][(data["^VIX1D_prior"] < vix_lower_bound)] = data["VIXY_ret"]

# SVXY
data["strat_ret"][(data["^VIX1D_prior"] > vix_upper_bound)] = data["SVXY_ret"]
data["strat_svxy_ret"][(data["^VIX1D_prior"] > vix_upper_bound)] = data["SVXY_ret"]
data["strat_svix_ret"][(data["^VIX1D_prior"] > vix_upper_bound)] = data["SVIX_ret"]


# VIX <> VIX3M
data["strat_vix>vix3m_ret"][data["^VIX_prior"] > data["^VIX3M_prior"]] = data["strat_ret"]
data["strat_vix<vix3m_ret"][data["^VIX_prior"] < data["^VIX3M_prior"]] = data["strat_ret"]


# Let's make a basic strategy list.
strategy_list = [
    #"SPY", "SVXY", "SVIX", "VIXY", "strat",
    "strat", "strat_vixy", "strat_svxy", "strat_svix",
]

vix_list = [
    "strat", "strat_vix>vix3m", "strat_vix<vix3m"
]

etf_list = ["SPY", "SVXY", "SVIX", "VIXY",]

for ticker in strategy_list:
    data[f"{ticker}_returns"] = portfolio_start * (1 + data[f"{ticker}_ret"]).cumprod()

for ticker in vix_list:
    data[f"{ticker}_returns"] = portfolio_start * (1 + data[f"{ticker}_ret"]).cumprod()

for ticker in etf_list:
    data[f"{ticker}_returns"] = portfolio_start * (1 + data[f"{ticker}_ret"]).cumprod()

plt.figure(dpi=150)
plt.xticks(rotation=45)
plt.suptitle(f"Geometric Returns for the Basic Strategy")
plt.title(f"Profit over time period") # Get the dates from X to Y as well.
legend_list = []
for ticker in ["strat"]:
    temp2 =f"{ticker} Return"
    plt.plot(data.index, data[f"{ticker}_returns"], label=temp2)
    legend_list.append(temp2)
plt.legend(legend_list)
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
plt.tight_layout()
plt.yscale(yscale)
plt.show()

# Let's look at the Strategy Components
plt.figure(dpi=150)
plt.xticks(rotation=45)
plt.suptitle(f"Geometric Returns for the Buy+Hold Vol ETFs and SPY")
plt.title(f"Profit over time period") # Get the dates from X to Y as well.
legend_list = []
for ticker in etf_list:
    temp2 =f"{ticker} Return"
    plt.plot(data.index, data[f"{ticker}_returns"], label=temp2)
    legend_list.append(temp2)
plt.legend(legend_list)
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
plt.tight_layout()
plt.yscale(yscale)
plt.show()

# Let's look at the Strategy Components
plt.figure(dpi=150)
plt.xticks(rotation=45)
plt.suptitle(f"Geometric Returns for the Strategies, Decomposed")
plt.title(f"Profit over time period") # Get the dates from X to Y as well.
legend_list = []
for ticker in strategy_list:
    temp2 =f"{ticker} Return"
    plt.plot(data.index, data[f"{ticker}_returns"], label=temp2)
    legend_list.append(temp2)
plt.legend(legend_list)
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
plt.tight_layout()
plt.yscale(yscale)
plt.show()

# Let's look at Returns split by "VIX regime"
plt.figure(dpi=150)
plt.xticks(rotation=45)
plt.suptitle(f"Geometric Returns for the Strategies based on VIX-VIX3M Regimes")
plt.title(f"Profit over time period") # Get the dates from X to Y as well.
legend_list = []
for ticker in vix_list:
    temp2 =f"{ticker} Return"
    plt.plot(data.index, data[f"{ticker}_returns"], label=temp2)
    legend_list.append(temp2)
plt.legend(legend_list)
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
plt.tight_layout()
plt.yscale(yscale)
plt.show()


# So, our ideal strategy is the following:
# VIX1D <= 10 Long VIXY
# VIX1D >= 15 Long SVIX
# Don't trade if ^VIX > ^VIX3M
data["strat_ideal_ret"] = 0
data["strat_ideal_ret"][(data["^VIX1D_prior"] <= vix_lower_bound)] = data["VIXY_ret"]
data["strat_ideal_ret"][(data["^VIX1D_prior"] >= vix_upper_bound)] = data["SVIX_ret"]
data["strat_ideal_ret"][data["^VIX_prior"] > data["^VIX3M_prior"]] = 0

final_list = [
    "strat_ideal", "VIXY", "SVIX", "SPY",
]
for ticker in final_list:
    data[f"{ticker}_returns"] = portfolio_start * (1 + data[f"{ticker}_ret"]).cumprod()


# We'll compare the ideal strategy to buy+hold of the components, and SPY
plt.figure(dpi=150)
plt.xticks(rotation=45)
plt.suptitle(f"Geometric Returns for the Strategies vs Buy+Hold")
plt.title(f"Profit over time period") # Get the dates from X to Y as well.
legend_list = []
for ticker in final_list:
    temp2 =f"{ticker} Return"
    plt.plot(data.index, data[f"{ticker}_returns"], label=temp2)
    legend_list.append(temp2)
plt.legend(legend_list)
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
plt.tight_layout()
plt.yscale(yscale)
plt.show()

# We can calculate the number of days we're trading:
data["strat_used"] = np.where(
    ((data["^VIX1D_prior"] <= vix_lower_bound) | (data["^VIX1D_prior"] >= vix_upper_bound))
    & (data["^VIX_prior"] < data["^VIX3M_prior"])
    ,1 ,0
)


# Now, let's get some statistics on our Strategy versus the buy+hold strategies of SPY and the trade components.
# I'm going to cheat a little against myself and have returns be 0% when the strategy is not invested, instead of the risk free rate.
print("What percent of time invested in Ideal Strategy: ", round(data["strat_used"].mean() * 100, 2), "%") # 50%
print("Strategy's Annual Return: ",round((100 * (((1 + data["strat_ideal_ret"].mean()) ** 252) - 1)),2), "%")
print("What percent of trades are profitable: ", round(np.where(data["strat_ideal_ret"][data["strat_ideal_ret"] != 0] > 0, 1, 0).mean() * 100, 2), "%") # 60%
print("What's the Avg Daily return for the strategy:", round(data["strat_ideal_ret"].mean()*100, 2), "%" ) # 0.33%
print("What's the Avg Daily return (while invested) for the strategy:", round(data["strat_ideal_ret"][data["strat_ideal_ret"] != 0].mean() * 100, 2), "%") # 0.73%
for ticker in final_list:
    print(f"{ticker} Sharpe Ratio: ", round((data[f"{ticker}_ret"].mean() - risk_free_rate) / data[f"{ticker}_ret"].std() * np.sqrt(252),2),
    f" Sortino Ratio: ", round((data[f"{ticker}_ret"].mean() - risk_free_rate) / data[data[f"{ticker}_ret"] < 0][f"{ticker}_ret"].std() * np.sqrt(252),2),
    f" Profit Factor: ", round(data[f"{ticker}_ret"][data[f"{ticker}_ret"] > 0].sum() / abs(data[f"{ticker}_ret"][data[f"{ticker}_ret"] < 0].sum()),2))



