"""
Trading minute 3:51-3:54 on the SPX

"""

import yfinance as yf
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import warnings
import time
import requests
import json
from urllib.request import urlopen
import ssl
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

warnings.filterwarnings("ignore")
polygon_api_key= "polygon_api_key"
fmp_api_key = "fmp_api_key"

used_stock = "SPY" # "I:SPX"
std_dev = 2 # what standard deviation move are we thinking?

trading_data = []


# Rolling Z-Score
def zscore(x, window):
    r = x.rolling(window=window)
    m = r.mean().shift(1)
    s = r.std(ddof=0).shift(1)
    z = (x-m)/s
    return z

def myfloor(x, base=5):
    return base * np.floor(x/base)

def myceiling(x, base=5):
    return base * np.ceil(x/base)

# We need to get SPX 1-minute bars.
# Make a function that gets and saves all daily 1-minute SPX data possible
def get_jsonparsed_data(url):
    response = urlopen(url, #cafile=certifi.where()
                       context=context)
    data = response.read().decode("utf-8")
    return json.loads(data)


# We can get 5 years of FMP data.
def get_spx_data_fmp():
    trading_data = []
    trading_dates = yf.download("SPY", start="2021-01-01", end="2030-01-01")["Volume"]
    trading_dates = list(trading_dates.index.astype(str).str[:10])
    for _date in trading_dates:
        time.sleep(0.10)
        data = pd.DataFrame(get_jsonparsed_data(f"https://financialmodelingprep.com/stable/historical-chart/1min?from={_date}&to={_date}&symbol=^GSPC&apikey={fmp_api_key}"))
        data = data[::-1]
        trading_data.append(data)
        print(_date, "done")
        #print(data.head().to_string())
    full_data = pd.concat(trading_data)
    full_data["date_str"] = full_data["date"].astype(str).str[:10]
    full_data["date"] = pd.to_datetime(full_data["date"])
    full_data["year"] = full_data["date"].dt.year
    full_data["month"] = full_data["date"].dt.month
    full_data["day"] = full_data["date"].dt.day
    full_data["hour"] = full_data["date"].dt.hour
    full_data["minute"] = full_data["date"].dt.minute
    full_data["day_name"] = full_data["date"].dt.day_name()

    # Get some percent changes.
    full_data["close2close"] = full_data["close"] - full_data["close"].shift(1)
    full_data["close2close_pct"] = full_data["close2close"] / full_data["close"].shift(1)
    # for Return from 3:51 Close to 3:44 Close.
    full_data["close2close_4"] = full_data["close"].shift(-4) - full_data["close"]
    full_data["close2close_4_pct"] = full_data["close2close_4"] / full_data["close"]
    # for Return from 3:51 CLose to 3:59 Close.
    full_data["close2close_9"] = full_data["close"].shift(-9) - full_data["close"]
    full_data["close2close_9_pct"] = full_data["close2close_4"] / full_data["close"]
    full_data["return_since_open"] = full_data['close'] - full_data.groupby("date_str")['open'].transform(lambda x: x.iloc[0])

    # Now let's get some more data here:
    # Z-scores of bar size, and the X-minute prior return of SPX.
    for i in [10, 20, 30, 60, 120, 240]:
        full_data[f"1_min_move_Z_score_{i}"] = round(zscore(full_data["close2close"], window=i),2)
        full_data[f"{i}_min_return_prior"] = (full_data["close"] - full_data["close"].shift(i)) / full_data["close"].shift(i)


    # Get the trading day number by month.
    spx_daily_data = yf.download("^SPX", start="2021-01-01", end="2030-01-01")
    spx_daily_data.columns = spx_daily_data.columns.droplevel(1)
    spx_daily_data["date"] = spx_daily_data.index.astype(str).str[:10]
    spx_daily_data["open2close_day"] = (spx_daily_data["Close"] - spx_daily_data["Open"]) / spx_daily_data["Open"]
    spx_daily_data["prior_Close_day"] = spx_daily_data["Close"].shift(1)
    spx_daily_data["close2close_day"] = (spx_daily_data["Close"] - spx_daily_data["prior_Close_day"]) / spx_daily_data["prior_Close_day"]
    # reform it with the current close price at the last bit after merging. Not sure about math on EMA's yet.
    for i in [5, 10, 20, 60]:
        #spx_daily_data[f"Close_ema_{i}"] = spx_daily_data["prior_Close_day"].ewm(span=i-1).mean()
        spx_daily_data[f"Close_sma_{i}"] = spx_daily_data["prior_Close_day"].rolling(i-1).mean()
    full_data = pd.merge(full_data, spx_daily_data, how="left", left_on="date_str", right_on="date")
    # Now get them with the updated number.
    for i in [5, 10, 20, 60]:
        #full_data[f"Close_ema_{i}_update"] = full_data[f"Close_ema_{i}"]
        full_data[f"Close_sma_{i}_update"] = (1/i)*full_data[f"close"] + ((i-1)/i)*full_data[f"Close_sma_{i}"]
    print(spx_daily_data.head().to_string())

    return full_data

# Old version using polygon. Only has about 2 years of 1-minute data.
def get_spx_data():
    trading_dates = yf.download("SPY", start="2023-06-01", end="2030-01-01")["Volume"]
    trading_dates = list(trading_dates.index.astype(str).str[:10])
    for _date in trading_dates:
        index_data = pd.json_normalize(requests.get(f"https://api.polygon.io/v2/aggs/ticker/I:SPX/range/1/minute/{_date}/{_date}?sort=asc&limit=50000&apiKey={polygon_api_key}").json()["results"]).set_index("t")
        index_data.index = pd.to_datetime(index_data.index, unit="ms", utc=True).tz_convert("America/New_York")
        trading_data.append(index_data)

    full_data = pd.concat(trading_data)
    full_data["date"] = full_data.index
    full_data["date_str"] = full_data["date"].astype(str).str[:10]
    full_data["year"] = full_data["date"].dt.year
    full_data["month"] = full_data["date"].dt.month
    full_data["day"] = full_data["date"].dt.day
    full_data["hour"] = full_data["date"].dt.hour
    full_data["minute"] = full_data["date"].dt.minute
    full_data["day_name"] = full_data["date"].dt.day_name()

    # Get some percent changes.
    full_data["close2close"] = full_data["c"] - full_data["c"].shift(1)
    full_data["close2close_pct"] = full_data["close2close"] / full_data["c"].shift(1)
    # for Return from 3:51 Close to 3:44 Close.
    full_data["close2close_4"] = full_data["c"].shift(-4) - full_data["c"]
    full_data["close2close_4_pct"] = full_data["close2close_4"] / full_data["c"]
    # for Return from 3:51 CLose to 3:59 Close.
    full_data["close2close_9"] = full_data["c"].shift(-9) - full_data["c"]
    full_data["close2close_9_pct"] = full_data["close2close_4"] / full_data["c"]
    full_data["return_since_open"] = full_data['c'] - full_data.groupby("date_str")['o'].transform(lambda x: x.iloc[0])

    # Now let's get some more data here:
    for i in [20, 60, 240]:
        full_data[f"1_min_move_Z_score_{i}"] = round(zscore(full_data["close2close"], window=i),2)

    # Now, cut down to the 15:50 1-minute candle. (and maybe the 3:55 later, I'm not certain.)
    full_data = full_data[(full_data["hour"]==15) & (full_data["minute"] == 50)]

    # Get the trading day number by month.
    full_data['day_num'] = full_data.groupby(["year", "month"])['date_str'].rank(method='first').astype(int)
    full_data['day_numr'] = full_data.groupby(["year", "month"])['date_str'].rank(method='first', ascending=False).astype(int)


    return full_data

#full_data = get_spx_data()
full_data = get_spx_data_fmp()
full_data.to_csv("./SPX_3:50_data.csv",header=True, mode='w')

#print(full_data.tail().to_string())

full_data = pd.read_csv(filepath_or_buffer="./SPX_3:50_data.csv")

# reformat
moc_data = pd.read_csv(filepath_or_buffer="./MOC Imbalance 3_50 data - Sheet1.csv")

full_data = pd.merge(full_data, moc_data, how="left", left_on="date_str", right_on="Date")

# Now, cut down to the 15:50 1-minute candle. (and maybe the 3:55 later? I'm not certain.)
full_data = full_data[(full_data["hour"]==15) & (full_data["minute"] == 50)]
full_data['day_num'] = full_data.groupby(["year", "month"])['date_str'].rank(method='first').astype(int)
full_data['day_numr'] = full_data.groupby(["year", "month"])['date_str'].rank(method='first', ascending=False).astype(int)
full_data["close_up_strike"] = myceiling(full_data["close"], base=5)
full_data["close_down_strike"] = myfloor(full_data["close"], base=5)
full_data["return_since_prior_Close"]= full_data["close"] - full_data["prior_Close_day"]

print(full_data.tail().to_string())

#print(full_data.tail(10).to_string())

# Okay, so what happens when we look at stocks that go above a x Z-Score, below -x Z-Score
# Try momentum and Z-score? Works really well.
above = full_data[(full_data["return_since_open"] > 0)
                  & (full_data["1_min_move_Z_score_60"] > std_dev)
]
below = full_data[(full_data["return_since_open"] < 0)
                  & (full_data["1_min_move_Z_score_60"] < -std_dev)
]
above["option_used"] = "C"
below["option_used"] = "P"


# So like, 30%-35% of the time we've got something interesting at 1xSTD, and 20% of the time at 2xSTD.
# And the average returns look pretty different.
print("Return Mean and Median:")
print(len(full_data),len(above), len(below))
print(full_data["close2close_4"].mean(), full_data["close2close_4"].std())
print(above["close2close_4"].mean(), above["close2close_4"].std())
print(below["close2close_4"].mean(), below["close2close_4"].std())

# Run code for a 1-sided T test to see if these 4-minute moves are different from mean=zero
pop_mean = 0
print("1-sided T-test for Above > 0 Mean return")
t_statistic_greater, p_value_greater = stats.ttest_1samp(above["close2close_4_pct"], pop_mean, alternative='greater')
print(f"One-sided (greater) t-test: t-statistic = {t_statistic_greater:.3f}, p-value = {p_value_greater:.3f}")

print("1-sided T-test for Below < 0 Mean return")
t_statistic_less, p_value_less = stats.ttest_1samp(below["close2close_4_pct"], pop_mean, alternative='less')
print(f"One-sided (greater) t-test: t-statistic = {t_statistic_less:.3f}, p-value = {p_value_less:.3f}")

# Let's get a list of dates we need:
temp = pd.concat([above, below], axis=0)
print(temp.tail().to_string())


option_returns = []

for index, row in temp.iterrows():
    #print(index, row["date_str"], row["close2close_4"], row["option_used"])
    # Now, we need to get the Long Call/Put for each item.
    temp_date = row["date_str"].replace("-", "")[2:]
    if row["option_used"] == "P":
        strike = row["close_down_strike"]
        strike = str(int(strike * 1000)).zfill(8)
    elif row["option_used"] == "C":
        strike = row["close_up_strike"]
        strike = str(int(strike * 1000)).zfill(8)
    else:
        strike = None
    time.sleep(0.05)
    p_url = f"https://api.polygon.io/v2/aggs/ticker/O:SPXW{temp_date}{row["option_used"]}{strike}/range/1/minute/{row["date_str"]}/{row["date_str"]}?adjusted=true&sort=asc&limit=10000&apiKey={polygon_api_key}"
    print(p_url)
    data = pd.DataFrame(get_jsonparsed_data(p_url).get("results"))
    if len(data) < 300:
        print("Empty Frame")
    # Set t so we can get year, month, day, hour, minute etc.
    else:
        data["date"] = pd.to_datetime(data["t"], unit="ms", utc=True).dt.tz_convert('US/Eastern')
        data["date"] = pd.to_datetime(data["date"])
        data["date_clip"] = pd.to_datetime(data["date"]).dt.date
        data["hour"] = data["date"].dt.hour
        data["minute"] = data["date"].dt.minute

        # Now, let's get rid of all data that isn't 3:50 to 3:54
        data = data[data["hour"] == 15]
        data = data[data["minute"].between(50,54)]
        #print(data.to_string())
        _return = data["c"].iloc[-1] - data["c"].iloc[0]
        _return_pct = _return / data["c"].iloc[0]
        _price_on_open = data["c"].iloc[0]
        #print(_return, _return_pct)

        # I need to create a dataframe of stuff for it.
        _df = pd.DataFrame(
            {"date": row["date_str"],
             "option": row["option_used"],
             "_return": _return,
             "_return_pct": _return_pct,
             "invested": _price_on_open # How much money did we spend on the option?
             }, index=[0]
        )
        option_returns.append(_df)

option_dataframe = pd.concat(option_returns)

print(option_dataframe["_return"].mean())
print(option_dataframe["_return_pct"].mean())
print(option_dataframe["_return"].sum())

option_dataframe = option_dataframe.sort_values(by='date')

option_dataframe_p = option_dataframe[option_dataframe["option"] == "P"]
option_dataframe_c = option_dataframe[option_dataframe["option"] == "C"]

# Now let's try returns where we use a constant amount invested.
# Investing $30 one day, and $1000 another due to option prices might not be ideal.
# invest up to $2000 per day?
investment_amount = 2000
for data in [option_dataframe, option_dataframe_c, option_dataframe_p]:
    data["_return_scale"] = data["_return"] * np.floor(2000.0/(data["invested"]*100))


#option_dataframe["portfolio_return"] = option_dataframe["_return"].cumsum()
i = 0
type_list = ["Overall", "Call", "Put"]
# Let's also get stats on the data:
for data in [option_dataframe, option_dataframe_c, option_dataframe_p]:
    data["portfolio_return"] = data["_return"].cumsum()
    data[f"drawdown"] = (data[f"_return"] - data["portfolio_return"].cummin()) / data[f"portfolio_return"].cummin()
    sharpe = data["_return"].mean() / data["_return"].std() * np.sqrt(252)
    sortino = data["_return"].mean() / np.where(data["_return"] < 0, data["_return"], 0).std() * np.sqrt(252)
    profit_factor = np.where(data["_return"] > 0,data["_return"], 0 ).sum() / abs(np.where(data["_return"] < 0, -data["_return"], 0).sum())
    max_drawdown = round(data[f"drawdown"].min() * 100, 2)
    print(f"Stats {type_list[i]}: \n Sharpe: {round(sharpe,2)}, Sortino: {round(sortino,2)}, Profit Factor: {round(profit_factor,2)}, Max Drawdown: ${round(max_drawdown,2)}")
    i +=1



plt.figure(dpi=150)
plt.xticks(rotation=45)
plt.suptitle(f"Returns for 3:51-3:54 SPX Option Trade {std_dev}x Std Dev")
plt.title(f"Profit over time period") # Get the dates from X to Y as well.
legend_list = []
i = 0
type_list = ["Overall", "Call", "Put"]
for _data in [option_dataframe, option_dataframe_c, option_dataframe_p]:
    temp2 =type_list[i]
    plt.plot(pd.to_datetime(_data["date"]), _data[f"_return"].cumsum()*100, label=temp2)
    legend_list.append(temp2)
    i+= 1
plt.legend(legend_list)
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
plt.tight_layout()
#plt.yscale()
plt.show()


# These numbers look a bit ridiculous, so I'm going to assume they won't be easily replicable.
# $6M in gains is a lot.
plt.figure(dpi=150)
plt.xticks(rotation=45)
plt.suptitle(f"Returns for 3:51-3:54 SPX Option Trade, {std_dev}x Std Dev $2K invested per trade")
plt.title(f"Profit over time period") # Get the dates from X to Y as well.
legend_list = []
i = 0
type_list = ["Overall", "Call", "Put"]
for _data in [option_dataframe, option_dataframe_c, option_dataframe_p]:
    temp2 =type_list[i]
    plt.plot(pd.to_datetime(_data["date"]), _data[f"_return_scale"].cumsum()*100, label=temp2)
    legend_list.append(temp2)
    i+= 1
plt.legend(legend_list)
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
plt.tight_layout()
#plt.yscale()
plt.show()
