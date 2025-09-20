import pandas as pd
import subprocess
import pandas_market_calendars as mcal # This might be an issue...
from datetime import datetime
from zoneinfo import ZoneInfo # For Python 3.9+; use pytz for older versions
import email_bot # not a library, another file.
import warnings
warnings.filterwarnings("ignore")

# Get the NYSE calendar
nyse = mcal.get_calendar('NYSE')

# Get today's date in 'America/New_York' timezone to match market hours
today = datetime.now(ZoneInfo('America/New_York')).date()

# Get the schedule for today
schedule = nyse.schedule(start_date=today, end_date=today)


if schedule.empty:
    print("The market is closed today (likely a weekend or holiday). We're not trading.")
else:
    # Extract the opening, closing, and current time
    market_close = schedule.iloc[0]['market_close']
    market_open = schedule.iloc[0]['market_open']
    now_et = datetime.now(ZoneInfo('America/New_York'))

    # Get the time differences:
    now_and_market_open = (pd.Timestamp(market_open) - pd.Timestamp(now_et)).total_seconds() / 60
    now_and_market_close = (pd.Timestamp(market_close) - pd.Timestamp(now_et)).total_seconds() / 60

    print(now_and_market_open, now_and_market_close)
    # If it's open today, what hour/minute does it close?
    print("Today's Market Close is ", market_close)
    print("Today's Market Open is ", market_open)
    print("Now is", now_et)
    # Is right NOW within 5 minutes of that close?
    # If so, run the Open trade bot. Then run the try_to_buy bot.
    if abs(now_and_market_close) <= 10:
        print("We'll run the open trade bot, we're within 10 minutes of Market Close for the day")
        subprocess.run(["python3","/path_to/order_bot.py"])
        email_bot.send_email_with("/path_to/try_to_buy.csv", body="ETF we're trying to buy and other info.")
        email_bot.send_email_with("/path_to/etf_snapshot.csv", body="ETF snapshot when we made the trade.")
    else:
        print("We're in a weird spot in the market? Not sure what's going on.")
        # no idea.
