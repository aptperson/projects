"""
Based on this paper:
https://download.ssrn.com/jfm/3fbddbee-7c8d-4b9e-9cc5-0aba15e26031-meca.pdf?response-content-disposition=inline&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEKP%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJGMEQCICeyNmPQMTrM%2FL4UdasNf1V%2FjCFJKClminkAUeC9J1kUAiBns13cVSPXw20AlEEjLSKWYf5Li%2F9XXfRyxD5pt9e3PCrGBQjL%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAQaDDMwODQ3NTMwMTI1NyIM5clIC4RjeKKK3ds8KpoFYtEr%2FRYGk5xTagUOIO0S%2FPJD5D65hQMOE0w7pa%2F6gz6lwEC5ADDWko0D0r7Bz%2BIMGMPjeIMr7WMitRqe0dTFGBEQ%2FI%2FWq%2FJ46PZsKxM34lEGEr%2Be1Y1DakTMUzSDiAe9chqFc%2FbnMruTa3ZBQHq%2BDHcT8rOqptLgF7g8TVerPNDOGIgUkJiwFmEDV2zMhP%2F8xcq6x1HeNn7pdBVACQ1Jw4Vsc2QVEaSUCnsKGstI5ScLlR22cyD%2B4XCkcj19txslgVQYqczHcyJzexnrEk%2BosCOYYlELSfrbXAR3JKblRh1ua8nhSzT6fT6xfOJ0deuDr9Xf5cTAKyQX0pU8%2F5%2B2tnN2r5qzGmAmUaTFSfkRauraQG4oQg%2BvXth0HTaV1Jo2027cyZh2QXiF1ebdTdadtnqSIR52WhwgoNBZ4hfc03VPOkMpY2UVu44gDKzFZcqSAdM74Cd0fN%2FOSH3jI3Fg8viAt%2FQD8Az30rZT7X1FeUw1MxGcWPYK9uW7By7MeUZT3J4HuXj4HFGiTz40%2Fb3eDoQ5aUB7CZ4v6ZTBUSJUWr3q5WSwJg8X0Ep5iNBgChjpIi9srVwYbTDeoWPpgfG%2BNh2np4q8ECmkN2i6%2FWmrorPPxv%2BdqVpILsgPgGoxCYuVcn1hJiy7mpSdQHmSNLPPwILdz9IZIaYXFeEIcO2MPHQJ2I%2BruZ%2BeX%2FELj2BVRzSrMKIeusXsHzLvshBvBmazuD1voxFB%2FFsRqfUuPq%2BgN44Vg2d1dJ80jmdUsPMWwlQtSlMvRYFlathCkGJZxYNfUc2%2BOoTyLJ89Wg9FzYzbYN%2BQcU1E5gor38Ieb36yQhUbgEM7muA3vf1X%2Fy9Ya%2Bradg9J8NWnXd7R%2FhsVs5GHa8fnYeMkkP1WzGhjMK%2Bhq8QGOrIB0IMns82yXDNrn9JTWv%2Bx%2Bfh6ms%2FP8TgU2XhfFATVzBrDlanLfcRCMPEGfn9ndUSK6ekENV9H9%2Bwd3hHsFWfUntyBUf3y8ZgLEZDyZp20h74jH9My6vFnxVqmiBDyysl3RxoMl5TJKAi%2Bzi%2BvmnidT3mct2bj6pUY29ppwr6k5dDq2g8ifXsrasa%2B7nSJj88L2YRa64MW1UWe8wANpJmgYkKJ9i0SdqqRhTSWu%2FhDFqGecA%3D%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20250731T032325Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-Amz-Credential=ASIAUPUUPRWEWJEVBKO3%2F20250731%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=9ab910861ccf7888a0ae7b92e7fa60c1aadd58fa7c5ab52f62c8bfb05ea6f558&abstractId=5294443

And this Blog Post (Definitely talk about it in your own post):
https://substack.com/@quantitativo/note/c-126735388

I used the dates provided by the Fed Itself for meetings and minutes:
https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm (for minutes release dates after 2020
https://www.federalreserve.gov/monetarypolicy/materials/ (for minutes release dates pre-2020
What about dates when FOMC Minutes are being released?
https://www.newyorkfed.org/medialibrary/media/research/epr/2013/0913rosa.pdf

According to the studies:
I'm assuming that a 1 day Pre-FOMC Short Straddle makes money
and a 1 day Post-FOMC Long Straddle makes money
I'm curious if the 1-day During-FOMC short straddle makes money

So we'd get ~48 trades per year of importance?
3*8 FOMC Meetings (Pre-During-Post)
3*8 FOMC Minutes releases (Pre-During+Post)


For Long-Volatility, it seems Straddles are fine. (Friday expiration)
Fort Short-Volatility, it's seems Iron Butterflies are good (Friday expiration, and general safety)

Not yet assuming slippage and commissions, but 1 Put+Call contract 8-40x per year. shouldn't be too onerous?
It's probably best to use 0DTEs?

"""

# Load Needed Libraries
# Get Every FOMC Date possible
# Make list of Pre-FOMC trading days
# May list of Post-FOMC trading days
# Get SPX daily Data (OHLC)?
# Get SPX option Data (OHLC) for the Straddles.


import pandas as pd
import yfinance as yf
import numpy as np
import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pandas_market_calendars import get_calendar
import json
import time
from urllib.request import urlopen
import ssl
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
import warnings
warnings.filterwarnings("ignore")

polygon_api_key = "Polygon API KEY HERE"
set_amount_risked = 1000 # set_amount_risked * 100 is the real amount in dollars.
show_polygon_links = False # Do we want to see each pulled link to polygon data?

## Functions:
def myround(x, base=5):
    return base * round(x/base)

def get_jsonparsed_data(url):
    response = urlopen(url, #cafile=certifi.where()
                       context=context)
    data = response.read().decode("utf-8")
    return json.loads(data)


# Just manually make the list for FOMC dates:
fomc_meeting_dates = [
    # 2025
    #"2025-01-28",
    "2025-01-29",
    #"2025-03-18",
    "2025-03-19",
    #"2025-05-06",
    "2025-05-07",
    #"2025-06-17",
    "2025-06-18",
    #"2025-07-29",
    "2025-07-30",
    #"2025-09-16",
    "2025-09-17",
    #"2025-10-28",
    "2025-10-29",
    #"2025-12-09",
    "2025-12-10",

    # 2024
    #"2024-10-30",
    "2024-01-31",
    #"2024-03-19",
    "2024-03-20",
    #"2024-04-30",
    "2024-05-01",
    #"2024-06-11",
    "2024-06-12",
    #"2024-07-30",
    "2024-07-31",
    #"2024-09-17",
    "2024-09-18",
    #"2024-11-06",
    "2024-11-07",
    #"2024-12-17",
    "2024-12-18",

    # 2023
    #"2023-01-31",
    "2023-02-01",
    #"2023-03-21",
    "2023-03-22",
    #"2023-05-02",
    "2023-05-03",
    #"2023-06-13",
    "2023-06-14",
    #"2023-07-25",
    "2023-07-26",
    #"2023-09-19",
    "2023-09-20",
    #"2023-10-31",
    "2023-11-01",
    #"2023-12-12",
    "2023-12-13",

    #2022
    #"2022-01-25",
    "2022-01-26",
    #"2022-03-15",
    "2022-03-16",
    #"2022-05-03",
    "2022-05-04",
    #"2022-06-14",
    "2022-06-15",
    #"2022-07-26",
    "2022-07-27",
    #"2022-09-20",
    "2022-09-21",
    #"2022-11-01",
    "2022-11-02",
    #"2022-12-13",
    "2022-12-14",

    # 2021
    #"2021-01-26",
    "2021-01-27",
    #"2021-03-16",
    "2021-03-17",
    #"2021-05-27",
    "2021-05-28",
    #"2021-06-15",
    "2021-06-16",
    #"2021-07-27",
    "2021-07-28",
    #"2021-09-21",
    "2021-09-22",
    #"2021-11-02",
    "2021-11-03",
    #"2021-12-14",
    "2021-12-15",

    # 2020
    #"2020-01-28",
    "2020-01-29",
    #"2020-03-03", "2020-03-15", # was unscheduled
    "2020-03-23",
    #"2020-04-28",
    "2020-04-29",
    #"2020-06-09",
    "2020-06-10",
    #"2020-07-28",
    "2020-07-29",
    #"2020-09-15",
    "2020-09-16",
    #"2020-11-04",
    "2020-11-05",
    #"2020-12-15",
    "2020-12-16",

    # 2019
    #"2019-01-29",
    "2019-01-30",
    #"2019-03-19",
    "2019-03-20",
    #"2019-04-30",
    "2019-05-01",
    #"2019-06-18",
    "2019-06-19",
    #"2019-07-30",
    "2019-07-31",
    #"2019-09-17",
    "2019-07-18",
    # "2019-10-04 unscheduled.
    #"2019-10-29",
    "2019-10-30",
    #"2019-12-10",
    "2019-12-11",

    # 2018
    #"2018-01-30",
    "2018-01-31",
    #"2018-03-20",
    "2018-03-21",
    #"2018-05-01",
    "2018-05-02",
    #"2018-06-12",
    "2018-06-13",
    #"2018-07-31",
    "2018-08-01",
    #"2018-09-25",
    "2018-09-26",
    #"2018-11-07",
    "2018-11-08",
    #"2018-12-18",
    "2018-12-19",

    # 2017
    #"2017-01-31",
    "2017-02-01",
    #"2017-03-14",
    "2017-03-15",
    #"2017-05-02",
    "2017-05-03",
    #"2017-06-13",
    "2017-06-14",
    #"2017-07-25",
    "2017-07-26",
    #"2017-09-19",
    "2017-09-20",
    #"2017-10-31",
    "2017-11-01",
    #"2017-12-12",
    "2017-12-13",

    # 2016
    #"2016-01-26",
    "2016-01-27",
    #"2016-03-15",
    "2016-03-16",
    #"2016-04-26",
    "2016-04-27",
    #"2016-06-14",
    "2016-06-15",
    #"2016-07-26",
    "2016-07-27",
    #"2016-09-20",
    "2016-09-21",
    #"2016-11-01",
    "2016-11-02",
    #"2016-12-13",
    "2016-12-14",

    # 2015
    #"2015-01-27",
    "2015-01-28",
    #"2015-03-17",
    "2015-03-18",
    #"2015-04-28",
    "2015-04-29",
    #"2015-06-17",
    "2015-06-18",
    #"2015-07-28",
    "2015-07-29",
    #"2015-09-16",
    "2015-09-17",
    #"2015-10-27",
    "2015-10-28",
    #"2015-12-15",
    "2015-12-16",

    # 2014
    "2014-01-28",
    #"2014-01-29",
    # 2014-03-04 unscheduled.
    #"2014-03-18",
    "2014-03-19",
    #"2014-04-29",
    "2014-04-30",
    #"2014-06-17",
    "2014-06-18",
    #"2014-07-29",
    "2014-07-30",
    #"2014-09-16",
    "2014-09-17",
    #"2014-10-28",
    "2014-10-29",
    #"2014-12-16",
    "2014-12-17",

    # 2013
    #"2013-01-29",
    "2013-01-30",
    #"2013-03-19",
    "2013-03-20",
    #"2013-04-30",
    "2013-05-01",
    #"2013-06-18",
    "2013-06-19",
    #"2013-07-30",
    "2013-07-31",
    #"2013-09-17",
    "2013-09-18",
    # "2013-10-16" unshceduled
    #"2013-10-29",
    "2013-10-30",
    #"2013-12-17",
    "2013-12-18",

    # 2012
    #"2012-01-24",
    "2024-01-25",
    "2012-03-13",
    #"2012-04-24",
    "2012-04-25",
    #"2012-06-19",
    "2012-06-20",
    #"2012-07-31",
    "2012-08-01",
    #"2012-09-12",
    "2012-09-13",
    #"2012-10-23",
    "2012-10-24",
    #"2012-12-11",
    "2012-12-12",

    # 2011
    #"2011-01-25",
    "2011-01-26",
    "2011-03-15",
    #"2011-04-26",
    "2011-04-27",
    #"2011-06-21",
    "2011-06-22",
    # "2011-08-01 Conference call?
    "2011-08-09",
    #"2011-09-20",
    "2011-09-21",
    #"2011-11-01",
    "2011-11-02",
    # 2011-11-28 Conference call?
    "2011-12-13"
    
    # 2010
    #"2010-01-26", 
    "2010-01-27",
    "2010-03-16",
    #"2010-04-27",
    "2010-04-28",
    # 2010-05-09 conference call?
    #"2010-06-22",
    "2010-06-23",
    "2010-08-10",
    "2010-09-21",
    # 2010-10-15
    #"2010-11-02",
    "2010-11-03",
    "2010-12-14",

    # 2009
    # "2009-01-16" conference call?
    #"2009-01-27",
    "2009-01-28",
    # 2009-02-09 conference call
    #"2009-03-17",
    "2009-03-18",
    #"2009-04-28",
    "2009-04-29",
    # 2009-06-03 conference call
    #"2009-06-23",
    "2009-06-24",
    #"2009-08-11",
    "2009-08-12",
    #"2009-09-22",
    "2009-09-23",
    #"2009-11-03",
    "2009-11-04",
    #"2009-12-15",
    "2009-12-16",

    # 2008
    # 2008-01-09 conference call
    # 2008-01-21 conference call
    "2008-01-29",
    #"2008-01-30",
    # 2008-03-10 conference call
    "2008-03-18",
    #"2008-04-29",
    "2008-04-30",
    #"2008-06-24",
    "2008-06-25",
    # 2008-07-24 conference call
    "2008-08-05",
    "2008-09-16",
    # 2008-09-29
    # 2008-10-07
    #"2008-10-28",
    "2008-10-29",
    #"2008-12-15",
    "2008-12-16",

    # 2007
    #"2007-01-30",
    "2007-01-31",
    #"2007-03-20",
    "2007-03-21",
    "2007-05-09",
    #"2007-06-27",
    "2007-06-28",
    "2007-08-07",
    # 2007-08-10
    # 2007-08-16
    "2007-09-18",
    #"2007-10-30",
    "2007-10-31",
    # 2007-12-06
    "2007-12-11",

    # 2006
    "2006-01-31",
    "2006-03-27",
    #"2006-03-28",
    "2006-05-10",
    #"2006-06-28",
    "2006-06-29",
    "2006-08-08",
    "2006-09-20",
    #"2006-10-24",
    "2006-10-25",
    "2006-12-12",

    # 2005
    #"2005-02-01",
    "2005-02-02",
    "2005-03-22",
    "2005-05-03",
    #"2005-06-29",
    "2005-06-30",
    "2005-08-09",
    "2005-09-20",
    "2005-11-01",
    "2005-12-13",
]

fomc_minutes_release_dates = [
    # 2025
    "2025-02-19",
    "2025-04-09",
    "2025-05-28",
    "2025-07-09",
    "2025-08-20",
    # 2024
    "2024-02-21",
    "2024-04-10",
    "2024-05-22",
    "2024-07-03",
    "2024-08-21",
    "2024-10-09",
    "2024-11-26",
    "2025-01-08",
    # 2023
    "2023-02-22",
    "2023-04-12",
    "2023-05-24",
    "2023-07-05",
    "2023-08-16",
    "2023-10-11",
    "2023-11-21",
    "2023-01-03",
    # 2022
    "2022-02-16",
    "2022-04-06",
    "2022-05-25",
    "2022-07-06",
    "2022-08-17",
    "2022-10-12",
    "2022-11-23",
    "2023-01-04",
    # 2021
    "2021-02-17",
    "2021-04-07",
    "2021-05-19",
    "2021-07-07",
    "2021-08-18",
    "2021-10-13",
    "2021-11-24",
    "2022-01-05",
    # 2020
    "2020-02-19",
    "2020-04-08", # Unscheduled meeting, but minutes were scheduled.
    "2020-05-20",
    "2020-07-01",
    "2020-08-19",
    "2020-10-07",
    "2020-11-25",
    "2021-01-06",
    # 2019
    "2020-01-03",
    "2019-11-20",
    "2019-10-09",
    "2019-10-04", # conference call minutes?
    "2019-08-21",
    "2019-07-10",
    "2019-05-22",
    "2019-04-10",
    "2019-02-20",
    # 2018
    "2019-01-09",
    "2018-11-29",
    "2018-10-17",
    "2018-08-22",
    "2018-07-05",
    "2018-05-23",
    "2018-04-11",
    "2018-02-21",
    # 2017
    "2018-01-03",
    "2017-10-11",
    "2017-08-16",
    "2017-07-05",
    "2017-05-24",
    "2017-04-05",
    "2017-02-22",
    # 2016
    "2017-01-04",
    "2016-11-23",
    "2016-10-12",
    "2016-08-17",
    "2016-07-06",
    "2016-05-18",
    "2016-04-06",
    "2016-02-17",
    # 2015
    "2016-01-06",
    "2015-11-18",
    "2015-10-08",
    "2015-08-19",
    "2015-07-08",
    "2015-05-20",
    "2015-04-08",
    "2015-02-18",
    "2015-01-07",
]


# WHAT ARE WE MEASURING:
#measure_list = fomc_meeting_dates # Meeting Dates Only
#measure_list = fomc_minutes_release_dates # Minutes Release Dates Only
measure_list = fomc_meeting_dates + fomc_minutes_release_dates # Both Meetings and Minutes released dates.

# WHEN DO WE START TRADING:
#start_date = "2022-01-01"
start_date = "2015-01-01" # Can also use

# ARE WE GOING LONG OR SHORT EACH PERIOD:
# 1 for Long Straddle/Long Iron Butterfly
# -1 for Short Straddle/Shot Iron Butterfly
pre_mult = -1
during_mult = -1
post_mult = 1


# ARE WE TRADING STRADDLES OR IRON CONDORS (HEDGING, THEREFORE NEED LONG OTM CALL AND PUT WINGS)
#iron_fly = False # Part of the data pulling function.

# WHAT IS THE VIX MULTIPLE FOR THE BUTTERFLY WINGS? (1X is for roughly 15 delta, 2X 5 delta?)
vix_multiple =  1 #is good enough?

# ARE WE TRADING: 0DTE or Nearest Friday Expiration?
#exp_type = "0DTE" # Option Expires that Day? Best after 2022.
exp_type = "Friday" # Nearest friday. Good after 2015.


print(len(fomc_meeting_dates), "FOMC meeting dates")
print(len(fomc_minutes_release_dates), "FOMC minutes release dates (for previous FOMC meeting)")
print(fomc_meeting_dates)
print(fomc_minutes_release_dates)

today = datetime.today().strftime('%Y-%m-%d')
# Get SPX daily data from 2005-01-01 to now:
benchmark_data = yf.download("^SPX", start=start_date, end=today)
benchmark_data.columns = benchmark_data.columns.droplevel(1)
#benchmark_data = pd.json_normalize(requests.get(f"https://api.polygon.io/v2/aggs/ticker/I:SPX/range/1/day/2005-01-01/2025-07-30?adjusted=true&sort=asc&limit=50000&apiKey={polygon_api_key}").json()["results"]).set_index("t")
#benchmark_data.index = pd.to_datetime(benchmark_data.index, unit="ms", utc=True).tz_convert("America/New_York")
benchmark_data["date"] = benchmark_data.index.strftime("%Y-%m-%d")
benchmark_data["prior_trading_day"] = benchmark_data["date"].shift(1)
benchmark_data["next_trading_day"] = benchmark_data["date"].shift(-1)
benchmark_data["weekday"] = benchmark_data.index.day_name()
benchmark_data["closest_strike"] = myround(benchmark_data["Open"], 5)
#print(benchmark_data.to_string())

# Get VIX data from 2005 to now?
# Use VIX Open data to size the short call and put?
vix_data = yf.download(tickers="^VIX",start=start_date, end="2030-01-01")[["Open", "High", "Low", "Close"]]
vix_data.columns = vix_data.columns.droplevel(1)
vix_data["date"] = vix_data.index.astype(str)
print(vix_data.tail().to_string())


# Get all Friday expiratons:
fridays = benchmark_data[benchmark_data["weekday"] == "Friday"]
fridays = fridays[["date"]]

# Let's make a function to pull meeting dates and the Open-to-Close returns for the day.

def get_o2c_returns(measure_list = [], trading_date="date", trading_mult = 1, iron_fly=False):
    fomc_dates =  benchmark_data[benchmark_data[trading_date].isin(measure_list)]
    fomc_dates = fomc_dates[["Open", "Close", "closest_strike", "date", "prior_trading_day", "next_trading_day", "weekday",]]
    option_returns = []

    for index, row in fomc_dates.iterrows():
        #  Depending on whether the expiration date is the same day or the nearest Friday:
        if exp_type == "Friday":
            temp_date = fridays[fridays["date"] >= row[trading_date]]
            if len(temp_date) < 1:
                continue
            temp_date = temp_date["date"].iloc[0].replace("-", "")[2:]
        elif exp_type == "0DTE":
            temp_date = row[trading_date].replace("-", "")[2:]
        # get the strike
        strike = str(int(row["closest_strike"] * 1000)).zfill(8)

        # Get the assumed move size from the VIX for that day
        vol_size = vix_data[vix_data["date"] == row[trading_date]]["Open"].iloc[0] * 0.01 / 15.89 * vix_multiple
        # Get the upper and lower estimate for closest strikes for the OTM wings.
        strike_up = row["closest_strike"] + myround(vol_size * row["closest_strike"], base=5)
        strike_down = row["closest_strike"] - myround(vol_size * row["closest_strike"], base=5)
        #print(vol_size, strike_up, strike, strike_down)
        strike_up = str(int(strike_up * 1000)).zfill(8)
        strike_down = str(int(strike_down * 1000)).zfill(8)
        print("traded day: ", row[trading_date], "expiration day: ", temp_date)
        time.sleep(0.02)
        p_url = f"https://api.polygon.io/v2/aggs/ticker/O:SPXW{temp_date}P{strike}/range/1/day/{row[trading_date]}/{row[trading_date]}?adjusted=true&sort=asc&limit=10000&apiKey={polygon_api_key}"
        c_url = f"https://api.polygon.io/v2/aggs/ticker/O:SPXW{temp_date}C{strike}/range/1/day/{row[trading_date]}/{row[trading_date]}?adjusted=true&sort=asc&limit=10000&apiKey={polygon_api_key}"
        p_url2 = f"https://api.polygon.io/v2/aggs/ticker/O:SPXW{temp_date}P{strike_down}/range/1/day/{row[trading_date]}/{row[trading_date]}?adjusted=true&sort=asc&limit=10000&apiKey={polygon_api_key}"
        c_url2 = f"https://api.polygon.io/v2/aggs/ticker/O:SPXW{temp_date}C{strike_up}/range/1/day/{row[trading_date]}/{row[trading_date]}?adjusted=true&sort=asc&limit=10000&apiKey={polygon_api_key}"
        if(show_polygon_links): print(p_url, c_url, p_url2, c_url2)
        data_c = pd.DataFrame(get_jsonparsed_data(c_url).get("results"))
        data_p = pd.DataFrame(get_jsonparsed_data(p_url).get("results"))
        data_c2 = pd.DataFrame(get_jsonparsed_data(c_url2).get("results"))
        data_p2 = pd.DataFrame(get_jsonparsed_data(p_url2).get("results"))
        #print(data_c2.to_string(), data_p2.to_string())
        if (len(data_c)  == 0) or (len(data_p) == 0):
            print("Empty Frame", row[trading_date],)
        elif (iron_fly) & ((len(data_c2)  == 0) or (len(data_p2) == 0)):
                print("Empty Frame", row[trading_date], )
        # Set t so we can get year, month, day, hour, minute etc.
        else:
            data_c["date"] = pd.to_datetime(data_c["t"], unit="ms", utc=True).dt.tz_convert('US/Eastern')
            data_c["date"] = pd.to_datetime(data_c["date"])

            data_p["date"] = pd.to_datetime(data_p["t"], unit="ms", utc=True).dt.tz_convert('US/Eastern')
            data_p["date"] = pd.to_datetime(data_p["date"])

            if (iron_fly):
                data_c["date"] = pd.to_datetime(data_c["t"], unit="ms", utc=True).dt.tz_convert('US/Eastern')
                data_c["date"] = pd.to_datetime(data_c["date"])

                data_p["date"] = pd.to_datetime(data_p["t"], unit="ms", utc=True).dt.tz_convert('US/Eastern')
                data_p["date"] = pd.to_datetime(data_p["date"])
                #print(data_c.to_string(), data_p.to_string(),data_c2.to_string(), data_p2.to_string(),)
            # Now make the variables:
            if iron_fly:
                _return = (data_c["c"].iloc[0] - data_c["o"].iloc[0] + data_p["c"].iloc[0] - data_p["o"].iloc[0]
                           - data_c2["c"].iloc[0] + data_c2["o"].iloc[0] - data_p2["c"].iloc[0] + data_p2["o"].iloc[0]
                           ) *trading_mult
                _return_pct = _return / (data_c["o"].iloc[0] + data_p["o"].iloc[0] - data_c2["o"].iloc[0] - data_p2["o"].iloc[0])
                _price_on_open = data_c["o"].iloc[0] + data_p["o"].iloc[0] - data_c2["o"].iloc[0] - data_p2["o"].iloc[0]
            else:
                _return = (data_c["c"].iloc[0] - data_c["o"].iloc[0] + data_p["c"].iloc[0] - data_p["o"].iloc[0])*trading_mult
                _return_pct = _return / (data_c["o"].iloc[0] + data_p["o"].iloc[0])
                _price_on_open = data_c["o"].iloc[0] + data_p["o"].iloc[0]
            #print(_return, _return_pct)

            # I need to create a dataframe of stuff for it.
            _df = pd.DataFrame(
                {"date":row[trading_date],
                 "strike": row["closest_strike"],
                 "_return": _return,
                 "_return_pct": _return_pct,
                 "invested": _price_on_open # How much money did we spend on the option?
                 }, index=[0]
            )
            option_returns.append(_df)

    option_dataframe = pd.concat(option_returns)
    # Let's make a "set $100K risked" return:
    option_dataframe["multiple"] = np.ceil(set_amount_risked /option_dataframe["invested"])
    option_dataframe["_return_set"] = option_dataframe["multiple"] * option_dataframe["_return"]
    option_dataframe_end = option_dataframe.copy()
    return option_dataframe_end.sort_values(by='date', ascending=True)


# Pull All three periods:
option_dataframe_pre = get_o2c_returns(measure_list=measure_list,
                                       trading_date="prior_trading_day",
                                       iron_fly=True,
                                       trading_mult=pre_mult)
option_dataframe_during = get_o2c_returns(measure_list=measure_list,
                                          trading_date="date",
                                          iron_fly=True,
                                          trading_mult=during_mult)
option_dataframe_post = get_o2c_returns(measure_list=measure_list,
                                        trading_date="next_trading_day",
                                        iron_fly=False,
                                        trading_mult=post_mult)

# Make a dataset for trading all days.
option_dataframe_total = pd.concat([option_dataframe_pre, option_dataframe_during, option_dataframe_post]).sort_values(by='date', ascending=True)


# Let's Take a look at the Metrics:
i = 0
name_list = ["Pre-FOMC", "During-FOMC", "Post-FOMC", "All Trades Together"]
for option_dataframe in [option_dataframe_pre, option_dataframe_during, option_dataframe_post,
              option_dataframe_total
              ]:
    print(option_dataframe.to_string())
    print(f"{name_list[i]} trade count: ", len(option_dataframe))
    print(f"{name_list[i]} returns: ")
    print("$", round(option_dataframe["_return"].sum()*100,2), " for 1 contract position.")
    print(f"{name_list[i]} returns Set: ")
    print(f"$", round(option_dataframe["_return_set"].sum()*100,2), " for set position.")
    print(f"{name_list[i]} Avg Return pct: ")
    print(round(option_dataframe["_return_pct"].mean() * 100, 2),"%")
    print(f"{name_list[i]} Sharpe:")
    print(round(option_dataframe["_return_pct"].mean()/option_dataframe["_return_pct"].std()*np.sqrt(252), 2))
    print(f"{name_list[i]} Sortino:")
    print(round(option_dataframe["_return_pct"].mean() / np.where(option_dataframe["_return_pct"] < 0, option_dataframe["_return_pct"], 0).std() * np.sqrt(252), 2))
    print(f"{name_list[i]} Profit Factor:")
    print(round(np.where(option_dataframe["_return_pct"]>0, option_dataframe["_return_pct"],0).sum()/np.where(option_dataframe["_return_pct"]<0, -option_dataframe["_return_pct"],0).sum(), 2))
    print("\n")
    i+=1



# Let's plot what happens over time.
plt.figure(dpi=150)
plt.xticks(rotation=45)
plt.suptitle(f"Returns 1 Contract Pre {pre_mult}X, {during_mult}X During, {post_mult}X Post FOMC Straddles, {exp_type} Expiration")
plt.title(f"Profit over time period") # Get the dates from X to Y as well.
legend_list = []
i = 0
type_list = ["Pre-FOMC",  "FOMC Date", "Post-FOMC", "Pre/During/Post Combo"]
for _data in [option_dataframe_pre,option_dataframe_during, option_dataframe_post,
              option_dataframe_total
              ]:
    temp2 =type_list[i]
    plt.plot(pd.to_datetime(_data["date"]), _data[f"_return"].cumsum()*100, label=temp2)
    legend_list.append(temp2)
    i+= 1
plt.legend(legend_list)
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
plt.tight_layout()
#plt.yscale()
plt.show()


plt.figure(dpi=150)
plt.xticks(rotation=45)
plt.suptitle(f"Returns Set Size Pre {pre_mult}X, {during_mult}X During, {post_mult}X Post FOMC Straddles, {exp_type} Expiration")
plt.title(f"Profit over time period") # Get the dates from X to Y as well.
legend_list = []
i = 0
type_list = ["Pre-FOMC",  "FOMC Date", "Post-FOMC", "Pre/During/Post Combo"]
for _data in [option_dataframe_pre, option_dataframe_during, option_dataframe_post,
              option_dataframe_total
              ]:
    temp2 =type_list[i]
    plt.plot(pd.to_datetime(_data["date"]), _data[f"_return_set"].cumsum()*100, label=temp2)
    legend_list.append(temp2)
    i+= 1
plt.legend(legend_list)
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
plt.tight_layout()
#plt.yscale()
plt.show()
