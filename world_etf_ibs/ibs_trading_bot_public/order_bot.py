"""
This bot will create Purchase orders at 3:59PM... -ish.

"""

import time
import json
import requests
import pandas as pd
import numpy as np


# In case I need to look at documentation again:
# https://api.tradestation.com/docs/specification#tag/MarketData/operation/GetOptionQuotes

CLIENT_ID = "get from TradeStation Customer Service"
CLIENT_SECRET = "Get from TradeStation Customer Service"
#REFRESH_TOKEN = "refresh token here" # refresh
refresh = False
# generate a refresh token
# run this line block and then copy/paste the login URL into your browser and login with your TradeStation credentials
#print(f'https://signin.tradestation.com/authorize?response_type=code&client_id={CLIENT_ID}&audience=https%3A%2F%2Fapi.tradestation.com&redirect_uri=http%3A%2F%2Flocalhost%3A3000&scope=openid%20MarketData%20profile%20ReadAccount%20Trade%20offline_access%20Matrix%20OptionSpreads')

# when you log in, you will get a "code" returned in the URL
# paste the "code" into this variable assignment statement and run this block
CODE = 'CODE that you get from URL'


if refresh == "DO THIS": # Don't unless there's an issue.
    # this request will get a new access token and refresh token
    # if desired, you can paste the refresh token above and rerun that code block
    # then after that, you can simply run the next code block anytime you need a new access token
    url = "https://signin.tradestation.com/oauth/token"

    payload=f'grant_type=authorization_code&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&code={CODE}&redirect_uri=http%3A%2F%2Flocalhost%3A3000'
    headers = {
      'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response_data = response.json()
    REFRESH_TOKEN = response_data['refresh_token']
    print('refresh_token: ', REFRESH_TOKEN)



REFRESH_TOKEN = "you get from the URL"

# this step will get a new access token using your refresh token when this function is called
def get_access_token():
    url = "https://signin.tradestation.com/oauth/token"

    payload=f'grant_type=refresh_token&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&refresh_token={REFRESH_TOKEN}'
    headers = {
      'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response_data = response.json()
    return response_data['access_token']

# SIM/MARGIN ACCOUNT URLS
#core_url = "https://sim-api.tradestation.com" # SIM
core_url = "https://api.tradestation.com" # MARGIN ACCOUNT

# get accounts
access_token = get_access_token() # get a new access token, only need to request it once when running this file.
url = f"{core_url}/v3/brokerage/accounts"
headers = {'Authorization': f'Bearer {access_token}' }
response = requests.request("GET", url, headers=headers)
json_data = response.json()
#print(json.dumps(json_data, indent=4, sort_keys=False))

# Here is the AccountID (Keep Secret)
account_id = "your account IDs for your account" # use MARGIN account
# get balances real time
url = f"{core_url}/v3/brokerage/accounts/{account_id}/balances"
headers = {"Authorization": f'Bearer {access_token}'}
response = requests.request("GET", url, headers=headers)
#print(response.text)

# Make the JSON a dict.
response = json.loads(response.text)
# What is the equity of the account?
print("Account Type: ", response["Balances"][0]["AccountType"])
print("Equity:", "$", response["Balances"][0]["Equity"])
# Don't need these.
# What is the CashBalance of the account?
#print("Cash Balance", "$", response["Balances"][0]["CashBalance"])
# What is the BuyingPower of the account?
#print("Buying Power", "$", response["Balances"][0]["BuyingPower"])
#if response["Balances"][0]["AccountType"]=="Margin":
#    # What is the overnight buying power? (margin only)
#    print("Overnight Buying Power", "$", response["Balances"][0]["BalanceDetail"]["OvernightBuyingPower"])



# SOME TRADE STUFF
# In order to get the quantity we want for each stock, we need the equity at start:
#equity = float(response["Balances"][0]["Equity"])
equity = float(response["Balances"][0]["Equity"])
# what percent of our equity are we using?
equity_percentage = 0.05 # increase/decrease the size of this position with your portfolio as needed
# How many different ETFs are we buying?
portfolio_size = 1.0 # if you want to have a more diverse portfolio of different ETFs, increase this. dumb name, sorry.
# How big is the minimum dollar allocation for these positions?
allocation = round(equity * equity_percentage / portfolio_size, 2)

"""
Note on TS's order code.
# OPG is market open
# GTC+ for good to Cancel plus extended
# Day+ for up to extended hours at 8pm
"""

# Make a function that makes an GTC+ buy order:
def open_buy_order(ticker="SPY", quantity=1, limit_price=0.01, access_token=""):
    url = f"{core_url}/v3/orderexecution/orders"
    payload = {
        "AccountID": account_id,
        "Symbol": ticker,
        "Quantity": str(quantity),
        "OrderType": "Limit",
        "TradeAction": "BUY",
        "LimitPrice": str(limit_price),
        "TimeInForce": {"Duration": "GCP"},
        "Route": "Intelligent"
    }
    headers = {
        "content-type": "application/json",
        "Authorization": f'Bearer {access_token}'
    }
    response = requests.request("POST", url, json=payload, headers=headers)
    print(response.text)

# Time from getting the TS data:
start_time = time.perf_counter()
# Chunk it if we're using a massive list, like > 90 tickers. Tradestation has a limit.
ticker_data = list(pd.read_csv(filepath_or_buffer="/path_to/etf_universe.csv")["ticker"])

#
tie_list = []
for ticker in ticker_data:
    url = f"https://api.tradestation.com/v3/marketdata/barcharts/{ticker}?unit=Daily&barsback=15"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.request("GET", url, headers=headers)
    #print(response.text)
    tie = pd.json_normalize(response.json()["Bars"])
    tie["Close"] = tie["Close"].astype(float)
    tie["mean_reversion"] = abs(tie["Close"] - tie["Close"].rolling(10).mean()) / tie["Close"].rolling(10).mean()
    tie["ticker"] = ticker
    # Get the latest Mean reversion
    tie = tie.tail(1)
    tie_list.append(tie)
ts_day_data = pd.concat(tie_list, axis=0)
#print(ts_day_data.to_string())

for _col in ["Open", "High", "Low", "Close", "TotalVolume"]:
    ts_day_data[_col] = ts_day_data[_col].astype(float)

# Create IBS and Mean Reversion metrics, picked 10 as a good length for the Moving Average.
ts_day_data["ibs"] = (ts_day_data["Close"] - ts_day_data["Low"])/(ts_day_data["High"] - ts_day_data["Low"])
# Remove anything with a 'VWAP' under $100000 traded today? or just use Close*Volume instead of VWAP.
ts_day_data["notional_value"] = ts_day_data["Close"] * ts_day_data["TotalVolume"]
ts_day_data = ts_day_data[ts_day_data["notional_value"].values >= 100000]
# Need high greater than low, don't want pointwise IBS calculations
ts_day_data = ts_day_data[ts_day_data["High"] > ts_day_data["Low"]]

ts_day_data = ts_day_data.sort_values(by=[ "ibs", "mean_reversion"], ascending=[True, False])
ts_day_data["rank"] = range(1, len(ts_day_data) + 1)
# Send a copy of this to my email:
ts_day_data.to_csv(path_or_buf="/path_to/etf_snapshot.csv")
#print(ts_day_data.to_string())

#print(ts_day_data[ts_day_data["rank"] <= 10].to_string())
#print(ts_day_data.to_string())

trading_data = list(ts_day_data[ts_day_data["rank"].values <= portfolio_size]["ticker"])
#print(trading_data.to_string())
#print(list(trading_data["Symbol"]))


def open_buy_orders(buy_list=["SPY"]):
    #access_token = get_access_token() # Only need to access this once.
    try_to_buy = []
    chunks_joined = ", ".join(buy_list)
    url = f"https://api.tradestation.com/v3/marketdata/quotes/{chunks_joined}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.request("GET", url, headers=headers)
    # print(response.text)
    data = pd.json_normalize(response.json()["Quotes"])
    for index, row in data.iterrows():
        ticker = row["Symbol"]
        limit_price = float(row["Close"])
        #rank = int(row["rank"])
        quantity = int(np.ceil(allocation / limit_price))
        bid = row["Bid"]
        ask = row["Ask"]
        print("Want to buy: ", ticker, " @", limit_price)
        open_buy_order(ticker=ticker, quantity=quantity, limit_price=round(limit_price, 2), access_token = access_token)
        temp = pd.DataFrame(
            {
                "ticker": ticker,
                "quantity": quantity,
                "limit_price":limit_price,
                "bid" : bid,
                "ask" : ask,
            }, index= [0]
        )
        try_to_buy.append(temp)
    try_to_buy = pd.concat(try_to_buy, axis=0)
    # get a record of what we just tried to buy so we can email it to ourselves.
    try_to_buy.to_csv(path_or_buf="/path_to/try_to_buy.csv")
    print(try_to_buy.to_string())
    return



### NOW RUN THE GLORIOUS BUYING CODE.
# we run this when we want to trade
open_buy_orders(buy_list=trading_data)

end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Execution time: {elapsed_time:.4f} seconds")
