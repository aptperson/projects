"""

Can volatility ETFs be traded on pre/during/post FOMC dates?
Volatility ETFs include VIXY, SVXY, SVIX.

What's interesting is the following:
FOMC days do well short Volatility (Long SVXY)
1-day Post-FOMC days do well long Volatility (Long VIXY)


"""

# LIBRARIES
import pandas as pd
import yfinance as yf
import numpy as np
import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

start_date = "2011-01-01"

risk_free_rate = 0.03/252

# Just manually make the list:
fomc_meeting_dates = [
    # 2025
    # "2025-01-28",
    "2025-01-29",
    # "2025-03-18",
    "2025-03-19",
    # "2025-05-06",
    "2025-05-07",
    # "2025-06-17",
    "2025-06-18",
    # "2025-07-29",
    "2025-07-30",
    # "2025-09-16",
    "2025-09-17",
    # "2025-10-28",
    "2025-10-29",
    # "2025-12-09",
    "2025-12-10",

    # 2024
    # "2024-10-30",
    "2024-01-31",
    # "2024-03-19",
    "2024-03-20",
    # "2024-04-30",
    "2024-05-01",
    # "2024-06-11",
    "2024-06-12",
    # "2024-07-30",
    "2024-07-31",
    # "2024-09-17",
    "2024-09-18",
    # "2024-11-06",
    "2024-11-07",
    # "2024-12-17",
    "2024-12-18",

    # 2023
    # "2023-01-31",
    "2023-02-01",
    # "2023-03-21",
    "2023-03-22",
    # "2023-05-02",
    "2023-05-03",
    # "2023-06-13",
    "2023-06-14",
    # "2023-07-25",
    "2023-07-26",
    # "2023-09-19",
    "2023-09-20",
    # "2023-10-31",
    "2023-11-01",
    # "2023-12-12",
    "2023-12-13",

    # 2022
    # "2022-01-25",
    "2022-01-26",
    # "2022-03-15",
    "2022-03-16",
    # "2022-05-03",
    "2022-05-04",
    # "2022-06-14",
    "2022-06-15",
    # "2022-07-26",
    "2022-07-27",
    # "2022-09-20",
    "2022-09-21",
    # "2022-11-01",
    "2022-11-02",
    # "2022-12-13",
    "2022-12-14",

    # 2021
    # "2021-01-26",
    "2021-01-27",
    # "2021-03-16",
    "2021-03-17",
    # "2021-05-27",
    "2021-05-28",
    # "2021-06-15",
    "2021-06-16",
    # "2021-07-27",
    "2021-07-28",
    # "2021-09-21",
    "2021-09-22",
    # "2021-11-02",
    "2021-11-03",
    # "2021-12-14",
    "2021-12-15",

    # 2020
    # "2020-01-28",
    "2020-01-29",
    # "2020-03-03", "2020-03-15", # was unscheduled
    "2020-03-23",
    # "2020-04-28",
    "2020-04-29",
    # "2020-06-09",
    "2020-06-10",
    # "2020-07-28",
    "2020-07-29",
    # "2020-09-15",
    "2020-09-16",
    # "2020-11-04",
    "2020-11-05",
    # "2020-12-15",
    "2020-12-16",

    # 2019
    # "2019-01-29",
    "2019-01-30",
    # "2019-03-19",
    "2019-03-20",
    # "2019-04-30",
    "2019-05-01",
    # "2019-06-18",
    "2019-06-19",
    # "2019-07-30",
    "2019-07-31",
    # "2019-09-17",
    "2019-07-18",
    # "2019-10-04 unscheduled.
    # "2019-10-29",
    "2019-10-30",
    # "2019-12-10",
    "2019-12-11",

    # 2018
    # "2018-01-30",
    "2018-01-31",
    # "2018-03-20",
    "2018-03-21",
    # "2018-05-01",
    "2018-05-02",
    # "2018-06-12",
    "2018-06-13",
    # "2018-07-31",
    "2018-08-01",
    # "2018-09-25",
    "2018-09-26",
    # "2018-11-07",
    "2018-11-08",
    # "2018-12-18",
    "2018-12-19",

    # 2017
    # "2017-01-31",
    "2017-02-01",
    # "2017-03-14",
    "2017-03-15",
    # "2017-05-02",
    "2017-05-03",
    # "2017-06-13",
    "2017-06-14",
    # "2017-07-25",
    "2017-07-26",
    # "2017-09-19",
    "2017-09-20",
    # "2017-10-31",
    "2017-11-01",
    # "2017-12-12",
    "2017-12-13",

    # 2016
    # "2016-01-26",
    "2016-01-27",
    # "2016-03-15",
    "2016-03-16",
    # "2016-04-26",
    "2016-04-27",
    # "2016-06-14",
    "2016-06-15",
    # "2016-07-26",
    "2016-07-27",
    # "2016-09-20",
    "2016-09-21",
    # "2016-11-01",
    "2016-11-02",
    # "2016-12-13",
    "2016-12-14",

    # 2015
    # "2015-01-27",
    "2015-01-28",
    # "2015-03-17",
    "2015-03-18",
    # "2015-04-28",
    "2015-04-29",
    # "2015-06-17",
    "2015-06-18",
    # "2015-07-28",
    "2015-07-29",
    # "2015-09-16",
    "2015-09-17",
    # "2015-10-27",
    "2015-10-28",
    # "2015-12-15",
    "2015-12-16",

    # 2014
    "2014-01-28",
    # "2014-01-29",
    # 2014-03-04 unscheduled.
    # "2014-03-18",
    "2014-03-19",
    # "2014-04-29",
    "2014-04-30",
    # "2014-06-17",
    "2014-06-18",
    # "2014-07-29",
    "2014-07-30",
    # "2014-09-16",
    "2014-09-17",
    # "2014-10-28",
    "2014-10-29",
    # "2014-12-16",
    "2014-12-17",

    # 2013
    # "2013-01-29",
    "2013-01-30",
    # "2013-03-19",
    "2013-03-20",
    # "2013-04-30",
    "2013-05-01",
    # "2013-06-18",
    "2013-06-19",
    # "2013-07-30",
    "2013-07-31",
    # "2013-09-17",
    "2013-09-18",
    # "2013-10-16" unshceduled
    # "2013-10-29",
    "2013-10-30",
    # "2013-12-17",
    "2013-12-18",

    # 2012
    # "2012-01-24",
    "2024-01-25",
    "2012-03-13",
    # "2012-04-24",
    "2012-04-25",
    # "2012-06-19",
    "2012-06-20",
    # "2012-07-31",
    "2012-08-01",
    # "2012-09-12",
    "2012-09-13",
    # "2012-10-23",
    "2012-10-24",
    # "2012-12-11",
    "2012-12-12",

    # 2011
    # "2011-01-25",
    "2011-01-26",
    "2011-03-15",
    # "2011-04-26",
    "2011-04-27",
    # "2011-06-21",
    "2011-06-22",
    # "2011-08-01 Conference call?
    "2011-08-09",
    # "2011-09-20",
    "2011-09-21",
    # "2011-11-01",
    "2011-11-02",
    # 2011-11-28 Conference call?
    "2011-12-13"

    # 2010
    # "2010-01-26", 
    "2010-01-27",
    "2010-03-16",
    # "2010-04-27",
    "2010-04-28",
    # 2010-05-09 conference call?
    # "2010-06-22",
    "2010-06-23",
    "2010-08-10",
    "2010-09-21",
    # 2010-10-15
    # "2010-11-02",
    "2010-11-03",
    "2010-12-14",

    # 2009
    # "2009-01-16" conference call?
    # "2009-01-27",
    "2009-01-28",
    # 2009-02-09 conference call
    # "2009-03-17",
    "2009-03-18",
    # "2009-04-28",
    "2009-04-29",
    # 2009-06-03 conference call
    # "2009-06-23",
    "2009-06-24",
    # "2009-08-11",
    "2009-08-12",
    # "2009-09-22",
    "2009-09-23",
    # "2009-11-03",
    "2009-11-04",
    # "2009-12-15",
    "2009-12-16",

    # 2008
    # 2008-01-09 conference call
    # 2008-01-21 conference call
    "2008-01-29",
    # "2008-01-30",
    # 2008-03-10 conference call
    "2008-03-18",
    # "2008-04-29",
    "2008-04-30",
    # "2008-06-24",
    "2008-06-25",
    # 2008-07-24 conference call
    "2008-08-05",
    "2008-09-16",
    # 2008-09-29
    # 2008-10-07
    # "2008-10-28",
    "2008-10-29",
    # "2008-12-15",
    "2008-12-16",

    # 2007
    # "2007-01-30",
    "2007-01-31",
    # "2007-03-20",
    "2007-03-21",
    "2007-05-09",
    # "2007-06-27",
    "2007-06-28",
    "2007-08-07",
    # 2007-08-10
    # 2007-08-16
    "2007-09-18",
    # "2007-10-30",
    "2007-10-31",
    # 2007-12-06
    "2007-12-11",

    # 2006
    "2006-01-31",
    "2006-03-27",
    # "2006-03-28",
    "2006-05-10",
    # "2006-06-28",
    "2006-06-29",
    "2006-08-08",
    "2006-09-20",
    # "2006-10-24",
    "2006-10-25",
    "2006-12-12",

    # 2005
    # "2005-02-01",
    "2005-02-02",
    "2005-03-22",
    "2005-05-03",
    # "2005-06-29",
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
    "2020-04-08",  # Unscheduled meeting, but minutes were scheduled.
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
    "2019-10-04",  # conference call minutes?
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

# Choose whether to use Meetings, Minutes, or both.
#fomc_dates = fomc_meeting_dates
#fomc_dates = fomc_minutes_release_dates
fomc_dates = fomc_meeting_dates + fomc_minutes_release_dates

# Now let's get our data:

today = datetime.today().strftime('%Y-%m-%d')
# Get SPX daily data from 2005-01-01 to now:
tickers = ["^SPX", "VIXY", "SVXY"]
all_data = []
for ticker in tickers:
    temp_data = yf.download(ticker, start=start_date, end=today)
    temp_data.columns = temp_data.columns.droplevel(1)
    #temp_data["Day_Return"] = (temp_data["Close"] - temp_data["Open"]) / temp_data["Open"]
    temp_data["Day_Return"] = (temp_data["Close"] - temp_data["Close"].shift(1)) / temp_data["Close"].shift(1)
    temp_data = temp_data.add_suffix(f"_{ticker}")
    all_data.append(temp_data)

all_data = pd.concat(all_data, axis = 1)
all_data["date"] = all_data.index.strftime("%Y-%m-%d")
all_data["prior_trading_day"] = all_data["date"].shift(1)
all_data["next_trading_day"] = all_data["date"].shift(-1)
all_data["weekday"] = all_data.index.day_name()

all_data["pre_FOMC_day"] = np.where(all_data["next_trading_day"].isin(fomc_dates), 1, 0)
all_data["FOMC_day"] = np.where(all_data["date"].isin(fomc_dates), 1, 0)
all_data["post_FOMC_day"] = np.where(all_data["prior_trading_day"].isin(fomc_dates), 1, 0)

# Now, let's limit to FOMC Pre/During/Post days
all_data = all_data[
    (all_data["pre_FOMC_day"] == 1) | (all_data["FOMC_day"] == 1) | (all_data["post_FOMC_day"] == 1)
]

# Let's look at the return data for each:
# Let's Take a look at the Metrics:
i = 0
name_list = ["Pre-FOMC", "During-FOMC", "Post-FOMC", "All Trades Together"]
for _data in [all_data[all_data["pre_FOMC_day"] == 1], all_data[all_data["FOMC_day"] == 1], all_data[all_data["post_FOMC_day"] == 1], all_data,]:
    for ticker in tickers:
        #print(_data.to_string())
        print(f"{name_list[i]} {ticker} trade count: ", len(_data))
        temp = ((1+_data[f"Day_Return_{ticker}"]).cumprod() - 1)[-1]
        print(f"{name_list[i]} {ticker} Total Returns: ", round(temp*100, 2), "%")
        print(f"{name_list[i]} {ticker} Percent of Trades Profitable: ", round(np.where(_data[f"Day_Return_{ticker}"] > 0, 1, 0).mean() * 100, 2), "%")
        print(f"{name_list[i]} {ticker} Avg Return pct: ", round(_data[f"Day_Return_{ticker}"].mean() * 100, 2),"%")
        print(f"{name_list[i]} {ticker} Sharpe:", round((_data[f"Day_Return_{ticker}"].mean()- risk_free_rate) /_data[f"Day_Return_{ticker}"].std()*np.sqrt(252), 2))
        print(f"{name_list[i]} {ticker} Sortino:", round((_data[f"Day_Return_{ticker}"].mean() - risk_free_rate) / np.where(_data[f"Day_Return_{ticker}"] < 0, _data[f"Day_Return_{ticker}"], 0).std() * np.sqrt(252), 2))
        print(f"{name_list[i]} {ticker} Profit Factor:", round(np.where(_data[f"Day_Return_{ticker}"]>0, _data[f"Day_Return_{ticker}"],0).sum()/np.where(_data[f"Day_Return_{ticker}"]<0, -_data[f"Day_Return_{ticker}"],0).sum(), 2))
        print("\n")
    i+=1


# Let's plot the Data:

# Pre-FOMC
plt.figure(dpi=150)
plt.xticks(rotation=45)
plt.suptitle(f"Pre-FOMC Returns for {tickers} 1-Day Return")
plt.title(f"Profit over time period") # Get the dates from X to Y as well.
legend_list = []
for ticker in tickers:
    temp2 = ticker
    temp_data = all_data[all_data["pre_FOMC_day"] ==1]
    plt.plot(pd.to_datetime(temp_data["date"]), (1 + temp_data[f"Day_Return_{ticker}"]).cumprod(), label=temp2)
    legend_list.append(temp2)
plt.legend(legend_list)
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
plt.tight_layout()
plt.show()



# During-FOMC
plt.figure(dpi=150)
plt.xticks(rotation=45)
plt.suptitle(f"FOMC Day Returns for {tickers} 1-Day Return")
plt.title(f"Profit over time period") # Get the dates from X to Y as well.
legend_list = []
for ticker in tickers:
    temp2 = ticker
    temp_data = all_data[all_data["FOMC_day"] ==1]
    plt.plot(pd.to_datetime(temp_data["date"]), (1 + temp_data[f"Day_Return_{ticker}"]).cumprod(), label=temp2)
    legend_list.append(temp2)
plt.legend(legend_list)
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
plt.tight_layout()
plt.show()



# Post-FOMC
plt.figure(dpi=150)
plt.xticks(rotation=45)
plt.suptitle(f"Post-FOMC Day Returns for {tickers} 1-Day Return")
plt.title(f"Profit over time period") # Get the dates from X to Y as well.
legend_list = []
for ticker in tickers:
    temp2 = ticker
    temp_data = all_data[all_data["post_FOMC_day"] ==1]
    plt.plot(pd.to_datetime(temp_data["date"]), (1 + temp_data[f"Day_Return_{ticker}"]).cumprod(), label=temp2)
    legend_list.append(temp2)
plt.legend(legend_list)
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
plt.tight_layout()
plt.show()

