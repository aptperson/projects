"""
Examine what happens to SPY over a weekend when Price is Above/Below EMA-10
Lay Quant
https://layquant.substack.com/

"""
import time
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from urllib.request import urlopen
import ssl
import json
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
import warnings
warnings.filterwarnings("ignore")

def get_jsonparsed_data(url):
    response = urlopen(url, #cafile=certifi.where()
                       context=context)
    data = response.read().decode("utf-8")
    return json.loads(data)

# Rolling RSI
def rsi(df, periods=20, ema=False, ref_point="close"):
    """
    Returns a pd.Series with the relative strength index.
    """
    close_delta = df[ref_point].diff()
    # Make two series: one for lower closes and one for higher closes
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)
    if ema == True:
        # Use exponential moving average
        ma_up = up.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
        ma_down = down.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
    else:
        # Use simple moving average
        ma_up = up.rolling(window=periods).mean()
        ma_down = down.rolling(window=periods).mean()
    rsi = ma_up / ma_down
    rsi = 100 - (100 / (1 + rsi))
    return rsi



polygon_api_key = "POLYGON_API_KEY"
ticker = "SPY"
date_start = "2016-06-01"
portfolio_risk = 0.02 # If you're making a position as a % of your portfolio, what % premium/portfolio do you take?


# if you're adding long calls+puts to prevent a massive loss, making it an Iron Butterfly, maybe subtract 10% from premium
# That's fair for 3-5 Delta Long Call+Put Options.
# We assume that these long options will usually go to zero, so it's just done to reduce premium sold.
hedge = 0.9

# Works for SPY, QQQ, IWM(sorta)
# IWM is flat, doesn't matter.
# GLD is bad and has too few instances. Commodities might work differently
# TLT is good, but has too few instances.

data = yf.download(ticker, start=date_start, #"2016-01-01", "2022-01-01", "1900-01-01",
                            end="2030-01-01")
data.columns = data.columns.droplevel(1)
# Return from Friday 4pm to Monday/Tuesday ~4pm
data["c2c"] = (data["Close"].shift(-1) - data["Close"]) / data["Close"]
data["Close_ema_10"] = data["Close"].ewm(span=10).mean()
data["Close_sma_10"] = data["Close"].rolling(10).mean()
data["rsi2"] = rsi(data,periods=2, ema=False, ref_point="Close")
data["above_ema"] = np.where(data["Close"] > data["Close_ema_10"], 1,0)
data["above_sma"] = np.where(data["Close"] > data["Close_sma_10"], 1,0)
#data["above_ema"] = np.where(data["rsi2"] > 50, 1, 0)
#data["above_sma"] = np.where(data["rsi2"] > 10, 1, 0)
data["date"] = data.index
data["weekday"] = data["date"].dt.day_name()
data["days_skip"] = (data["date"].shift(-1) - data["date"]).dt.days - 1
data["is_Friday"] = np.where(data["weekday"] == "Friday", 1, 0)


# Friday-Oriented:
data_old = data
# Skipped Days (weekends, holidays)
#data = data[data["days_skip"] > 1]
data = data[data["weekday"] == "Friday"]
#data = data[data["weekday"] != "Friday"]
print(data.to_string())

test1 = data[data["above_ema"] == 1]
test2 = data[data["above_ema"] == 0]

print(ticker, "general data \n",
      "Instance Count", len(data), "\n",
      "Avg:", round(data["c2c"].mean(),4), "\n",
      "StDev:", round(data["c2c"].std(),4), "\n",
      "Skew:", round(data["c2c"].skew(),4), "\n",
      "Kurtosis:", round(data["c2c"].kurt(),4), "\n",
      )

print(ticker, "Above SMA-10 data \n",
      "Instance Count", len(test1), "\n",
      "Avg:", round(test1["c2c"].mean(),4), "\n",
      "StDev:", round(test1["c2c"].std(),4), "\n",
      "Skew:", round(test1["c2c"].skew(),4), "\n",
      "Kurtosis:", round(test1["c2c"].kurt(),4), "\n",
      )

print(ticker, "Below SMA-10 data \n",
      "Instance Count", len(test2), "\n",
      "Avg:", round(test2["c2c"].mean(),4), "\n",
      "StDev:", round(test2["c2c"].std(),4), "\n",
      "Skew:", round(test2["c2c"].skew(),4), "\n",
      "Kurtosis:", round(test2["c2c"].kurt(),4), "\n",
      )



plt.title(f"{ticker} Chart of c2c returns")
plt.plot(data.index, data["c2c"])
plt.show()


plt.title(f"{ticker} Chart of c2c 1-day returns")
plt.plot(test1.index, test1["c2c"], label="Above 10-SMA")
plt.plot(test2.index, test2["c2c"], label="Below 10-SMA")
plt.legend(["Above 10-SMA", "Below 10-SMA"])
plt.show()

# cumulative returns
plt.title(f"{ticker} Chart of c2c 1-day returns")
plt.plot(test1.index, (1+test1["c2c"]).cumprod(), label="Above 10-SMA")
plt.plot(test2.index, (1+test2["c2c"]).cumprod(), label="Below 10-SMA")
plt.legend(["Above 10-SMA", "Below 10-SMA"])
plt.show()


sns.histplot(data=data, x='c2c', hue='above_ema', multiple='layer', kde=True)
plt.title(f'{ticker} C2C Friday-Monday Histogram by Above/Below EMA-10')
plt.show()


# Pull Daily Expected move data from Polygon:
straddle_dates = list(data.index.strftime("%Y-%m-%d"))

data_list = []

for i in range(0, len(straddle_dates)-1):
    print("Date Opened: ", straddle_dates[i], "Expiration: ", straddle_dates[i + 1])
    date = straddle_dates[i]
    date2 = straddle_dates[i+1]
    time.sleep(0.05)
    try:
        underlying_url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{date}/2025-10-23?adjusted=true&sort=asc&limit=25000&apiKey={polygon_api_key}"
        # print(underlying_url)
        underlying_temp = pd.DataFrame(get_jsonparsed_data(underlying_url).get("results"))
        underlying_temp['date'] = pd.to_datetime(underlying_temp['t'], unit='ms').dt.date.astype(str)
        # print(underlying_temp.to_string())

        # print(date)
        stock_price = underlying_temp[underlying_temp["date"] == str(date2)]
        # print(stock_price)
        stock_price = stock_price["c"].iloc[0]
        stock_price2 = underlying_temp[underlying_temp["date"] == str(date)]
        stock_price2 = stock_price2["c"].iloc[0]
        # print(stock_price2)
        url = (f"https://api.polygon.io/v3/reference/options/contracts?underlying_ticker={ticker}&"
               f"order=asc&"
               f"limit=250&"
               f"expiration_date.gte={date}&"
               f"expiration_date.lte={date2}&"
               f"strike_price.gte={stock_price - 50}&"
               f"strike_price.lte={stock_price + 50}&"
               f"sort=strike_price&"
               f"expired=true&"
               f"contract_type=call&"
               f"apiKey={polygon_api_key}")
        # print(url)
        temp = pd.DataFrame(get_jsonparsed_data(url).get("results"))
        temp["current_price"] = stock_price
        temp["dist_to_price"] = abs(temp["strike_price"] - temp["current_price"])
        # print(temp.to_string())
        temp = temp[temp["strike_price"] == np.floor(temp["strike_price"])]
        temp = temp[temp["expiration_date"] != date]
        temp = temp[temp["expiration_date"] == min(temp["expiration_date"])]
        temp = temp.nsmallest(1, columns="dist_to_price")
        strike_price = temp["strike_price"].iloc[0]
        # we need the ticker. And can replace Call with Put in the ticker name.
        # print(temp.to_string())
        call_ticker = temp["ticker"].iloc[0]
        put_ticker = temp["ticker"].iloc[0].replace("C", "P")
        # print(call_ticker, put_ticker)

        # then we get the lifetime bars
        call_url = f"https://api.polygon.io/v2/aggs/ticker/{call_ticker}/range/1/day/{date}/{date2}?adjusted=true&sort=asc&limit=250&apiKey={polygon_api_key}"
        # print(call_url)
        put_url = f"https://api.polygon.io/v2/aggs/ticker/{put_ticker}/range/1/day/{date}/{date2}?adjusted=true&sort=asc&limit=250&apiKey={polygon_api_key}"
        # print(put_url)

        call_data = pd.DataFrame(get_jsonparsed_data(call_url)).get("results")
        call_start = call_data[0]["c"]
        call_end = call_data[1]["c"]
        # print(call_data.to_string())
        put_data = pd.DataFrame(get_jsonparsed_data(put_url)).get("results")
        put_start = put_data[0]["c"]
        put_end = put_data[1]["c"]
        # print(put_data.to_string())
        # print(call_start, put_start, call_end,put_end)
        ma_temp = data_old[data_old["date"] == date]
        above_ema = ma_temp["above_ema"].iloc[0]
        above_sma = ma_temp["above_sma"].iloc[0]
        on_friday = ma_temp["is_Friday"].iloc[0]
        print(f"{ticker} price at open:", stock_price, "epx_date: ", date2, "date_trade_opened: ", date, "Straddle Open:",
              call_start + put_start, "Straddle Close: ", call_end + put_end)
        data_list.append(
            pd.DataFrame(
                {"ticker": ticker,
                 "stock_price": stock_price,
                 "stock_price_close": stock_price2,
                 "strike_price": strike_price,
                 "exp_date": date2,
                 "date_opened": date,
                 "straddle_abs": (call_start + put_start),
                 "straddle_pct": (call_start + put_start)/stock_price,
                 "above_ema": above_ema,
                 "above_sma": above_sma,
                 "opened_on_friday": on_friday
                 },
                index=[0]
            )
        )
    except:
        print("problem at:", date, date2)

data_full = pd.concat(data_list)
data_full = data_full[::-1]

# Now, we need to look at average % size of Straddles for each group.
print("\n")
data_full_friday = data_full[data_full["opened_on_friday"] == 1]
print(f"Friday 1DTE Straddle Size (Pct of {ticker} Underlying)")
print(len(data_full_friday), round(data_full_friday["straddle_pct"].mean()*100,2), round(data_full_friday["straddle_pct"].std()*100,2))

data_full_weekday = data_full[data_full["opened_on_friday"] == 0]
print(f"Weekday 1DTE Straddle Size (Pct of {ticker} Underlying)")
print(len(data_full_weekday), round(data_full_weekday["straddle_pct"].mean()*100,2), round(data_full_weekday["straddle_pct"].std()*100,2))


data_full_above = data_full[data_full["above_ema"] == 1]
print(f"Above 10-EMA 1DTE Straddle Size (Pct of {ticker} Underlying)")
print(len(data_full_above), round(data_full_above["straddle_pct"].mean()*100,2), round(data_full_above["straddle_pct"].std()*100,2))

data_full_below = data_full[data_full["above_ema"] == 0]
print(f"Below 10-EMA 1DTE Straddle Size (Pct of {ticker} Underlying)")
print(len(data_full_below), round(data_full_below["straddle_pct"].mean()*100,2), round(data_full_below["straddle_pct"].std()*100,2))


data_full_friday_above = data_full[(data_full["opened_on_friday"] == 1) & (data_full["above_ema"] == 1)]
print(f"Friday Above 10-EMA 1DTE Straddle Size (Pct of {ticker} Underlying)")
print(len(data_full_friday_above), round(data_full_friday_above["straddle_pct"].mean()*100,2), round(data_full_friday_above["straddle_pct"].std()*100,2))

data_full_friday_below = data_full[(data_full["opened_on_friday"] == 1) & (data_full["above_ema"] == 0)]
print(f"Friday Below 10-EMA 1DTE Straddle Size (Pct of {ticker} Underlying)")
print(len(data_full_friday_below), round(data_full_friday_below["straddle_pct"].mean()*100,2), round(data_full_friday_below["straddle_pct"].std()*100,2))

data_full_weekday_above = data_full[(data_full["opened_on_friday"] == 0) & (data_full["above_ema"] == 1)]
print(f"Weekday Above 10-EMA 1DTE Straddle Size (Pct of {ticker} Underlying)")
print(len(data_full_weekday_above), round(data_full_weekday_above["straddle_pct"].mean()*100,2), round(data_full_weekday_above["straddle_pct"].std()*100,2))

data_full_weekday_below = data_full[(data_full["opened_on_friday"] == 0) & (data_full["above_ema"] == 0)]
print(f"Weekday Below 10-EMA 1DTE Straddle Size (Pct of {ticker} Underlying)")
print(len(data_full_weekday_below), round(data_full_weekday_below["straddle_pct"].mean()*100,2), round(data_full_weekday_below["straddle_pct"].std()*100,2))


# Now:
# We need end-of-week dates for each week from 2015
# We need start-of-week dates for each week from 2015
# Start of Week:
rng = pd.date_range(start=date_start, end="2025-10-20", freq="B") # 'B' for business day
prices = pd.DataFrame(np.random.rand(len(rng)), index=rng, columns=['date'])
# Print the original DataFrame to see the daily data
#print("Original daily prices:\n", prices)
# Resample the data on a weekly basis, anchoring the week to Sunday ('W-SUN').
# The .first() method then selects the first data point within each new week.
first_trading_day = prices.resample('W-MON').first()
first_trading_day = list(first_trading_day.index.strftime("%Y-%m-%d"))
first_trading_day.reverse()
print(first_trading_day)

dates = pd.date_range(start=date_start, end='2025-10-20', freq='B') # 'B' for business days
data = {'Close': range(len(dates))}
df = pd.DataFrame(data, index=dates)
# Resample to weekly frequency and get the last value for each week
# 'W' resamples to the end of the week (Sunday by default)
# '.last()' selects the last entry within each weekly group, which will be the last trading day
last_trading_day = df.resample('W-FRI').last()
last_trading_day = list(last_trading_day.index.strftime("%Y-%m-%d"))
last_trading_day.reverse()
print(last_trading_day)

data_list = []

for i in range(0, len(first_trading_day)):
    time.sleep(0.1)
    try:
        print("Expiration: ", first_trading_day[i], "Date Opened: ", last_trading_day[i+1])
        date = last_trading_day[i+1]
        date2 = first_trading_day[i]
        # redo this, using https://polygon.io/docs/rest/options/contracts/all-contracts
        # get closest strike price
        # then use it to get Friday Close price, and Monday/Tuesday Close price for ATM Call and Put

        # Get the stock prices for SPY

        underlying_url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{date}/2025-10-23?adjusted=true&sort=asc&limit=25000&apiKey={polygon_api_key}"
        #print(underlying_url)
        underlying_temp = pd.DataFrame(get_jsonparsed_data(underlying_url).get("results"))
        underlying_temp['date'] = pd.to_datetime(underlying_temp['t'], unit='ms').dt.date.astype(str)
        #print(underlying_temp.to_string())

        #print(date)
        stock_price = underlying_temp[underlying_temp["date"] == str(date2)]
        #print(stock_price)
        stock_price = stock_price["c"].iloc[0]
        stock_price2 = underlying_temp[underlying_temp["date"] == str(date)]
        stock_price2= stock_price2["c"].iloc[0]
        #print(stock_price2)
        url = (f"https://api.polygon.io/v3/reference/options/contracts?underlying_ticker={ticker}&"
               f"order=asc&"
               f"limit=250&"
               f"expiration_date.gte={date}&"
               f"expiration_date.lte={date2}&"
               f"strike_price.gte={stock_price-50}&"
               f"strike_price.lte={stock_price+50}&"
               f"sort=strike_price&"
               f"expired=true&"
               f"contract_type=call&"
               f"apiKey={polygon_api_key}")
        #print(url)
        temp = pd.DataFrame(get_jsonparsed_data(url).get("results"))
        temp["current_price"] = stock_price
        temp["dist_to_price"] = abs(temp["strike_price"] - temp["current_price"])
        #print(temp.to_string())
        temp = temp[temp["strike_price"] == np.floor(temp["strike_price"])]
        temp = temp[temp["expiration_date"] != date]
        temp = temp[temp["expiration_date"] == min(temp["expiration_date"])]
        temp = temp.nsmallest(1, columns="dist_to_price")
        strike_price = temp["strike_price"].iloc[0]
        # we need the ticker. And can replace Call with Put in the ticker name.
        #print(temp.to_string())
        call_ticker= temp["ticker"].iloc[0]
        put_ticker = temp["ticker"].iloc[0].replace("C", "P")
        #print(call_ticker, put_ticker)

        # then we get the lifetime bars
        call_url = f"https://api.polygon.io/v2/aggs/ticker/{call_ticker}/range/1/day/{date}/{date2}?adjusted=true&sort=asc&limit=250&apiKey={polygon_api_key}"
        #print(call_url)
        put_url = f"https://api.polygon.io/v2/aggs/ticker/{put_ticker}/range/1/day/{date}/{date2}?adjusted=true&sort=asc&limit=250&apiKey={polygon_api_key}"
        #print(put_url)

        call_data = pd.DataFrame(get_jsonparsed_data(call_url)).get("results")
        call_start = call_data[0]["c"]
        call_end = call_data[1]["c"]
        #print(call_data.to_string())
        put_data = pd.DataFrame(get_jsonparsed_data(put_url)).get("results")
        put_start = put_data[0]["c"]
        put_end = put_data[1]["c"]
        #print(put_data.to_string())
        #print(call_start, put_start, call_end,put_end)
        ma_temp = data_old[data_old["date"] == date]
        above_ema = ma_temp["above_ema"].iloc[0]
        above_sma = ma_temp["above_sma"].iloc[0]
        print(f"{ticker} price at open:", stock_price, "epx_date: ", date2 , "date_trade_opened: ", date, "Straddle Open:", call_start+put_start,"Straddle Close: ", call_end+put_end)
        data_list.append(
            pd.DataFrame(
                {"ticker": ticker,
                 "stock_price": stock_price,
                 "stock_price_close": stock_price2,
                 "strike_price": strike_price,
                 "exp_date": date2,
                 "date_opened":date,
                 "straddle_open": (call_start+put_start)*hedge,
                 "straddle_close": call_end+put_end,
                 "profit": (call_start+put_start) - (call_end+put_end),
                 "abs_profit": hedge*(call_start+put_start) - abs(strike_price - stock_price2) ,
                 "above_ema": above_ema,
                 "above_sma": above_sma,
                 },
                index=[0]
            )
        )
    except:
        print("problem at:", date, date2)

data_full = pd.concat(data_list)
data_full = data_full[::-1]

# What if we looked at % return on profit?
data_full["pct_return"] = data_full["abs_profit"]/data_full["straddle_open"]

print(data_full.to_string())

above_ema = data_full[data_full["above_ema"]==1]
above_sma = data_full[data_full["above_sma"]==1]
below_ema = data_full[data_full["above_ema"]==0]
below_sma = data_full[data_full["above_sma"]==0]

# What about profits from holding until the exact second?
print("Above EMA/SMA profits if held to 4pm, Average and Sum per Contract:")
print(len(above_ema), len(above_sma))
print("EMA Avg Profit Per Contract: ", above_ema["abs_profit"].mean(), "\n",
      "EMA Avg Premium Per Contract:", above_ema["straddle_open"].mean(), "\n",
      "EMA St Dev Profit: ",  above_ema["abs_profit"].std(),"\n",
      "EMA Profit Per Contract: ", np.where(above_ema["abs_profit"] > 0, above_ema["abs_profit"], 0).sum(),"\n",
      "EMA Loss Per Contract: ", np.where(above_ema["abs_profit"] <= 0, above_ema["abs_profit"], 0).sum(),"\n",
      "EMA Win Rate: ",round(np.where(above_ema["abs_profit"] > 0, 1, 0).mean()*100,2),"\n",
      "EMA Total Profit:", above_ema["abs_profit"].sum()),"\n",
print("SMA Avg Profit Per Contract: ",  above_sma["abs_profit"].mean(),"\n",
      "SMA Avg Premium Per Contract:", above_sma["straddle_open"].mean(), "\n",
      "SMA St Dev Profit: ",  above_sma["abs_profit"].std(),"\n",
      "SMA Profit Per Contract: ", np.where(above_sma["abs_profit"] > 0, above_sma["abs_profit"], 0).sum(),"\n",
      "SMA Loss Per Contract: ", np.where(above_sma["abs_profit"] <= 0, above_sma["abs_profit"], 0).sum(),"\n",
      "SMA Win Rate: ",round(np.where(above_sma["abs_profit"] > 0, 1, 0).mean()*100,2),"\n",
      "SMA Total Profit:",above_sma["abs_profit"].sum()),"\n",

print("Below EMA/SMA profits if held to 4pm, Average and Sum per Contract:")
print(len(below_ema), len(below_sma))
print("EMA Avg Profit Per Contract: ", below_ema["abs_profit"].mean(),"\n",
      "EMA Avg Premium Per Contract:", below_ema["straddle_open"].mean(), "\n",
      "EMA St Dev Profit: ",  below_ema["abs_profit"].std(),"\n",
      "EMA Profit Per Contract: ", np.where(below_ema["abs_profit"] > 0, below_ema["abs_profit"], 0).sum(),"\n",
      "EMA Loss Per Contract: ", np.where(below_ema["abs_profit"] <= 0, below_ema["abs_profit"], 0).sum(),"\n",
      "EMA Win Rate: ",round(np.where(below_ema["abs_profit"] > 0, 1, 0).mean()*100,2),"\n",
      "EMA Total Profit:", below_ema["abs_profit"].sum()),"\n",
print("SMA Avg Profit Per Contract: ",  below_sma["abs_profit"].mean(),"\n",
      "SMA Avg Premium Per Contract:", below_sma["straddle_open"].mean(), "\n",
      "SMA St Dev Profit: ",  below_sma["abs_profit"].std(),"\n",
      "SMA Profit Per Contract: ", np.where(below_sma["abs_profit"] > 0, below_sma["abs_profit"], 0).sum(), "\n",
      "SMA Loss Per Contract: ", np.where(below_sma["abs_profit"] <= 0, below_sma["abs_profit"], 0).sum(), "\n",
      "SMA Win Rate: ",round(np.where(below_sma["abs_profit"] > 0, 1, 0).mean()*100,2),"\n",
      "SMA Total Profit:",below_sma["abs_profit"].sum()),"\n",


# Chart
plt.figure(dpi=150)
plt.xticks(rotation=45)
plt.suptitle(f"Weekend Straddle Abs Returns (1x Contract) for {ticker}")
plt.title(f"Profit over time period") # Get the dates from X to Y as well.
plt.plot(pd.to_datetime(above_ema["exp_date"]), (above_ema[f"abs_profit"]).cumsum(), label="Above-EMA")
plt.plot(pd.to_datetime(below_ema["exp_date"]), (below_ema[f"abs_profit"]).cumsum(), label="Below-EMA")
plt.plot(pd.to_datetime(above_sma["exp_date"]), (above_sma[f"abs_profit"]).cumsum(), label="Above-SMA")
plt.plot(pd.to_datetime(below_sma["exp_date"]), (below_sma[f"abs_profit"]).cumsum(), label="Below-SMA")
plt.legend(["Above-EMA", "Below-EMA", "Above-SMA", "Below-SMA"])
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
plt.tight_layout()
plt.show()

plt.figure(dpi=150)
plt.xticks(rotation=45)
plt.suptitle(f"Weekend Straddle Cumulative Pct Returns for {ticker}")
plt.title(f"Profit over time period") # Get the dates from X to Y as well.
plt.plot(pd.to_datetime(above_ema["exp_date"]), (1+above_ema[f"pct_return"]*portfolio_risk).cumprod(), label="Above-EMA")
plt.plot(pd.to_datetime(below_ema["exp_date"]), (1+below_ema[f"pct_return"]*portfolio_risk).cumprod(), label="Below-EMA")
plt.plot(pd.to_datetime(above_sma["exp_date"]), (1+above_sma[f"pct_return"]*portfolio_risk).cumprod(), label="Above-SMA")
plt.plot(pd.to_datetime(below_sma["exp_date"]), (1+below_sma[f"pct_return"]*portfolio_risk).cumprod(), label="Below-SMA")
plt.legend(["Above-EMA", "Below-EMA", "Above-SMA", "Below-SMA"])
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
plt.tight_layout()
plt.show()


