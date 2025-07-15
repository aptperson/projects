
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
from datetime import datetime, timedelta
import time
import requests
import json
from urllib.request import urlopen
import ssl
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
warnings.filterwarnings("ignore")

fmp_api_key = "FMP_KEY"
polygon_api_key = "POLYGON_KEY"

# It works, I just need a larger stop loss. And maybe a trailing stop loss. (50%???)
ticker = "QQQ"
buy_slippage = 0.02
sell_slippage = 0.02
stop_loss = 0.50 # the general stop loss %
trailing_stop = 0.50 # the trailing stop loss %
opening_range = 15 # minutes after open we're establishing the Opening Range
trading_length = 500# how many trading days are we analyzing
portfolio = 2000


def get_jsonparsed_data(url):
    response = urlopen(url, #cafile=certifi.where()
                       context=context)
    data = response.read().decode("utf-8")
    return json.loads(data)


def get_variable_name(obj, namespace):
    for name, value in namespace.items():
        if value is obj:
            return name
    return None

# Make a function that pulls as much 1-minute data as possible for QQQ and ^VIX
def pull_and_save_data(ticker="SPY", start_date="2022-01-01", end_date="2025-07-11"):
    date_list = yf.download(tickers="SPY", start=start_date, end=end_date)["Volume"]
    trading_dates = list(date_list.index.astype(str).str[:10])
    price_data = []
    for _date in trading_dates:
        print(_date)
        time.sleep(0.1)
        url = f"https://financialmodelingprep.com/stable/historical-chart/1min?from={_date}&to={_date}&symbol={ticker}&apikey={fmp_api_key}"
        temp = pd.DataFrame(get_jsonparsed_data(url))
        if len(temp) > 0:
            price_data.append(temp)
    price_data = pd.concat(price_data)
    print(price_data.head())
    price_data.to_csv(path_or_buf=f"./{ticker}_1min.csv")
    return



# Now pull 1-minute data for VIX and QQQ. I don't think they have VNX/VXN whatever it's called?
#pull_and_save_data(ticker="QQQ")
#pull_and_save_data(ticker="^VIX")

qqq = pd.read_csv(filepath_or_buffer=f"./{ticker}_1min.csv")
vix = pd.read_csv(filepath_or_buffer=f"./^VIX_1min.csv")

for data in [qqq, vix]:
    data["date_str"] = data["date"].astype(str).str[:10]
    data["date"] = pd.to_datetime(data["date"])
    data["year"] = data["date"].dt.year
    data["month"] = data["date"].dt.month
    data["day"] = data["date"].dt.day
    data["hour"] = data["date"].dt.hour
    data["minute"] = data["date"].dt.minute
    data["day_name"] = data["date"].dt.day_name()

# Sort and order stuff:
qqq = qqq.sort_values(by='date', ascending=True)
qqq["bar"] = qqq.groupby("date_str").cumcount() + 1
vix = vix.sort_values(by='date', ascending=True)
vix["bar"] = vix.groupby("date_str").cumcount() + 1

# create the Opening Range high and low and then remerge
qqq["OR_high"] = qqq.groupby("date_str")["high"].rolling(window=opening_range).max().reset_index(level=0, drop=True)
qqq["OR_low"] = qqq.groupby("date_str")["low"].rolling(window=opening_range).min().reset_index(level=0, drop=True)
or_values = qqq[qqq["bar"] == opening_range]
or_values = or_values.rename(columns={'OR_high': 'OR_high_day', 'OR_low': 'OR_low_day'})
or_values = or_values[["date_str", "OR_high_day", "OR_low_day"]]
print(or_values.head())

qqq = pd.merge(qqq, or_values, how="left", left_on="date_str", right_on="date_str")
qqq["OR_high_day"][qqq["bar"] <=opening_range -1] = np.nan
qqq["OR_low_day"][qqq["bar"] <=opening_range - 1] = np.nan

qqq["above_OR_high"] = np.where(qqq["close"].shift(1) > qqq["OR_high_day"], 1, 0)
qqq["below_OR_low"] = np.where(qqq["close"].shift(1) < qqq["OR_low_day"], 1, 0)
qqq["OR_both"] = qqq["above_OR_high"] + qqq["below_OR_low"]
# Find when there's a trigger
qqq["OR_trigger"] = (qqq.groupby('date_str')["OR_both"].cumsum() == 1).astype(int)
qqq["OR_call_trigger"] = (qqq.groupby('date_str')["above_OR_high"].cumsum() == 1).astype(int)
qqq["OR_put_trigger"] = (qqq.groupby('date_str')["below_OR_low"].cumsum() == 1).astype(int)

# Let's get rid of the last 4 minutes, because we want to sell by 3:55 EST.
qqq = qqq[~((qqq["hour"] == 15) & (qqq["minute"] >= 56))]


# now let's add VIX Close values? And get VIX daily values.

vix_daily = yf.download("^VIX", start="2000-01-01", end="2030-01-01")[["Close", "Open"]]
vix_daily.columns = vix_daily.columns.droplevel(1)
vix_daily["date_str"] = vix_daily.index.astype(str).str[:10]
vix_daily["vix_prior_close"] = vix_daily["Close"].shift(1)
vix_daily["vix_close2open"] = vix_daily["Open"] - vix_daily["vix_prior_close"]
print(vix_daily.head())
# Assume we're buying on the open of the next minute.
qqq = pd.merge(qqq, vix_daily, how="left", left_on="date_str", right_on="date_str")
# Now let's merge minute-by-minute VIX
qqq = pd.merge(qqq, vix[["date", "open", "low", "high", "close"]].add_suffix("_vix"), how="left", left_on="date", right_on="date_vix" )
# Want to make sure this is < 0 when we're buying calls or puts?
# Or do we even care????
qqq["vix_return_from_close"] = (qqq["close_vix"] - qqq["vix_prior_close"]) / qqq["vix_prior_close"]


# Currently VIX drop/gain for both.
qqq["above_OR_high_vix"] = np.where((qqq["close"].shift(1) > qqq["OR_high_day"]) & (qqq["vix_return_from_close"] < 0), 1, 0)
qqq["below_OR_low_vix"] = np.where((qqq["close"].shift(1) < qqq["OR_low_day"]) & (qqq["vix_return_from_close"] < 0), 1, 0)
qqq["OR_both_vix"] = qqq["above_OR_high_vix"] + qqq["below_OR_low_vix"]
# Find when there's a trigger
qqq["OR_trigger_vix"] = (qqq.groupby('date_str')["OR_both_vix"].cumsum() == 1).astype(int)
qqq["OR_call_trigger_vix"] = (qqq.groupby('date_str')["above_OR_high_vix"].cumsum() == 1).astype(int)
qqq["OR_put_trigger_vix"] = (qqq.groupby('date_str')["below_OR_low_vix"].cumsum() == 1).astype(int)


# How we determine the "strike" price that should roughly be 0.7 Delta?? ($2 of strikes below current price?)
qqq["call_strike"] = qqq["close"].round() - 2
qqq["put_strike"] = qqq["close"].round() + 2

# Let's see if we can just make a P/C column for QQQ
qqq["put/call"] = ""
qqq["put/call_vix"] = ""
qqq["put/call"][(qqq["OR_trigger"] == 1) & (qqq["OR_trigger"].shift(1) == 0) & (qqq["OR_call_trigger"] == 1)] = "C"
qqq["put/call"][(qqq["OR_trigger"] == 1) & (qqq["OR_trigger"].shift(1) == 0) & (qqq["OR_put_trigger"] == 1)] = "P"
qqq["put/call_vix"][(qqq["OR_trigger_vix"] == 1) & (qqq["OR_trigger_vix"].shift(1) == 0) & (qqq["OR_call_trigger_vix"] == 1)] = "C"
qqq["put/call_vix"][(qqq["OR_trigger_vix"] == 1) & (qqq["OR_trigger_vix"].shift(1) == 0) & (qqq["OR_put_trigger_vix"] == 1)] = "P"

# Make a regular, and vix-effected dataset.
qqq_reg = qqq[(qqq["OR_trigger"] == 1) & (qqq["OR_trigger"].shift(1) == 0)]

# Let's try seeing what happens if we trade when the VIX is down at the ORB trigger point?
qqq_vix= qqq[(qqq["OR_trigger_vix"] == 1) & (qqq["OR_trigger_vix"].shift(1) == 0)]

# Take a look at the regular and VIX-dependent data
print(qqq_reg.tail(50).to_string())
print(qqq_vix.tail(50).to_string())


# Make lists to hold our results from the data.
regular_stop_list = []
regular_stop_vix_list = []
trailing_stop_list = []
trailing_stop_vix_list = []
no_stops_list = []
no_stops_vix_list = []

# Need to make this a function so it can be looped.
def get_option_data(ticker="QQQ", _date="2025-07-09",
                    data_group=qqq_reg,
                    stop_list = regular_stop_list,
                    trailing_list = trailing_stop_list,
                    no_stops_list=no_stops_list):
    # So let's get Calls at a certain value.
    temp = data_group[data_group["date_str"] == _date].tail(1)
    if len(temp) == 0:
        print("Skipped Day")
        return
    print(temp.to_string())
    ticker = ticker
    _date = temp["date_str"].iloc[0]
    _date_strip = _date.replace("-", "")
    _date_strip = _date_strip[2:]
    option_type = temp["put/call"].iloc[0]
    if option_type == "P":
        strike = temp["put_strike"].iloc[0]
    else:
        strike = temp["call_strike"].iloc[0]
    hour = temp["hour"].iloc[0]
    minute = temp["minute"].iloc[0]
    strike = str(int(strike * 1000)).zfill(8)
    #print(strike)
    time.sleep(0.05)
    p_url = f"https://api.polygon.io/v2/aggs/ticker/O:{ticker}{_date_strip}{option_type}{strike}/range/1/minute/{_date}/{_date}?adjusted=true&sort=asc&limit=10000&apiKey={polygon_api_key}"

    # Get the URL and the data strip for the option.
    print(p_url)
    data = pd.DataFrame(get_jsonparsed_data(p_url).get("results"))
    if len(data) == 0:
        print("Empty Frame")
        return
    # Set t so we can get year, month, day, hour, minute etc.
    data["date"] = pd.to_datetime(data["t"], unit="ms", utc=True).dt.tz_convert('US/Eastern')
    data["date"] = pd.to_datetime(data["date"])
    data["date_clip"] = pd.to_datetime(data["date"]).dt.date
    data["hour"] = data["date"].dt.hour
    data["minute"] = data["date"].dt.minute

    # Let's remove everything after 3:55 PM EST, and everything before 9:35 AM EST
    # for 60 minutes, I need something different.
    data = data[~((data["hour"] == 9) & (data["minute"] <= 29 + opening_range))]
    data = data[~((data["hour"] == 15) & (data["minute"] >= 55))]
    data = data[~(data["hour"] == 16)]

    # Now let's find the start time for our ORB strategy
    data = data[~((data["hour"] == hour) & (data["minute"] <= minute))]

    # Our first price, what we buy at is the Open price. (can also do mid of high and low? add slippage? I'm not sure)
    data["open_price"] = data["o"].iloc[0] + buy_slippage
    data["return"] = (data["c"] - data["open_price"]) / data["open_price"]
    data["price_return"] = (data["c"] - data["open_price"] - sell_slippage) * 100 # Our actual money counting.
    data["static_stop_loss"] = -stop_loss
    #print(data.to_string())
    data["dynamic_stop_loss"] = np.where(data["return"].cummax() - trailing_stop > -stop_loss, data["return"].cummax() - trailing_stop, -stop_loss)
    data["close_trailing"] = (np.where(data["return"] <= data["dynamic_stop_loss"], 1, 0).cumsum() == 1).astype(int)
    # Get rid of duplicates hits for a stop loss.:
    data.loc[data['close_trailing'].duplicated(keep='first'), 'close_trailing'] = 0
    data["close_stop_loss"] = (np.where(data["return"] <= data["static_stop_loss"], 1, 0).cumsum() == 1).astype(int)
    data.loc[data['close_stop_loss'].duplicated(keep='first'), 'close_stop_loss'] = 0

    # If our stop losses don't trigger, we just use the last time to close out
    if data["close_stop_loss"].sum() == 0:
        data["close_stop_loss"].iloc[-1] = 1
    if data["close_trailing"].sum() == 0:
        data["close_trailing"].iloc[-1] = 1
    #print(data.to_string())
    data["no_stops"] = 0
    data["no_stops"].iloc[-1] = 1
    # now. What do we have for returns?
    end_sl = data[data["close_stop_loss"] == 1]
    end_trail = data[data["close_trailing"] == 1]
    no_stops = data[data["no_stops"] == 1]
    #print(end_trail.to_string())
    #print(end_sl.to_string())

    # Now add the 2 items to the list.
    stop_list.append(end_sl)
    trailing_list.append(end_trail)
    no_stops_list.append(no_stops)
    return


for date in qqq_reg["date_str"].iloc[-trading_length:]:
    print(date)
    get_option_data(_date=date,data_group=qqq_reg, stop_list=regular_stop_list, trailing_list=trailing_stop_list, no_stops_list=no_stops_list)
    get_option_data(_date=date, data_group=qqq_vix, stop_list=regular_stop_vix_list, trailing_list=trailing_stop_vix_list, no_stops_list=no_stops_vix_list)

regular_data = pd.concat(regular_stop_list)
trailing_data = pd.concat(trailing_stop_list)
no_stops_data = pd.concat(no_stops_list)
regular_vix_data = pd.concat(regular_stop_vix_list)
trailing_vix_data = pd.concat(trailing_stop_vix_list)
no_stops_vix_data = pd.concat(no_stops_vix_list)


# Now, let's see if we can make a strip for this.
data_names = ["regular", "trailing", "no stops", "regular vix", "trailing vix", "no stops vix"]
i = 0
for data in [regular_data, trailing_data, no_stops_data, regular_vix_data, trailing_vix_data, no_stops_vix_data]:
    data["portfolio_return"] = data["price_return"].cumsum()
    data[f"drawdown"] = (data[f"price_return"] - data["portfolio_return"].cummin()) / data[f"portfolio_return"].cummin()
    sharpe = data["price_return"].mean() / data["price_return"].std() * np.sqrt(252)
    sortino = data["price_return"].mean() / np.where(data["price_return"] < 0, data["price_return"], 0).std() * np.sqrt(252)
    profit_factor = np.where(data["price_return"] > 0,data["price_return"], 0 ).sum() / abs(np.where(data["price_return"] < 0, -data["price_return"], 0).sum())
    max_drawdown = round(data[f"drawdown"].min() * 100, 2)
    print(f"Stats {data_names[i]}: \n Sharpe: {round(sharpe,2)}, Sortino: {round(sortino,2)}, Profit Factor: {round(profit_factor,2)}, Max Drawdown: ${round(max_drawdown,2)}")
    i +=1

print(regular_data.tail().to_string())
print(trailing_data.tail().to_string())
print(no_stops_data.tail().to_string())

print(regular_vix_data.tail().to_string())
print(trailing_vix_data.tail().to_string())
print(no_stops_vix_data.tail().to_string())




# We'll compare the ideal strategy to buy+hold of the components, and SPY
plt.figure(dpi=150)
plt.xticks(rotation=45)
plt.suptitle(f"Returns for the QQQ Strategies")
plt.title(f"Profit over time period") # Get the dates from X to Y as well.
legend_list = []
tip = ["regular", "trailing", "no stops"]
i = 0
for ticker in [regular_data, trailing_data, no_stops_data]:
    temp2 =f"{tip[i]} Return"
    plt.plot(ticker["date_clip"], ticker[f"portfolio_return"], label=temp2)
    legend_list.append(temp2)
    i += 1
plt.legend(legend_list)
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
plt.tight_layout()
#plt.yscale()
plt.show()


plt.figure(dpi=150)
plt.xticks(rotation=45)
plt.suptitle(f"Returns for the QQQ Strategies when VIX move < 0")
plt.title(f"Profit over time period") # Get the dates from X to Y as well.
legend_list = []
tip = ["regular", "trailing", "no_stop"]
i = 0
for ticker in [regular_vix_data, trailing_vix_data, no_stops_vix_data]:
    temp2 =f"{tip[i]} Return"
    plt.plot(ticker["date_clip"], ticker[f"portfolio_return"], label=temp2)
    legend_list.append(temp2)
    i += 1
plt.legend(legend_list)
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
plt.tight_layout()
#plt.yscale()
plt.show()

