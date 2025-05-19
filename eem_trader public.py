from polygon import BaseClient
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

# when adjusting period_start and end, keep in mind that SPY, EEM/TLT/EMB, and EDC/SPXL have different starts to their trading histories.
# I'm using 2010 for the starting date because the strategies have an absurdly profitable run from 2008-2010 that I'm not sure will be replicated for a while.
yscale = "log" # linear charts are not very illustrative over long periods of time.
period_start = "2010-01-01"
period_end = "2025-05-01"
risk_free_rate = 0.03 / 252
portfolio_start = 1
use = "yfinance" # or "polygon"
client = BaseClient("polygon API code here")
# want the hour 15, 50-minute timeframe.
def get_daily_near_closing_value(ticker=None, hour=15, minute=50):
    aggs = []
    for a in client.list_aggs(
            ticker,
            5,
            "minute",
            "2000-01-01",
            "2030-01-01",
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


ticker_list = ["SPY", "SPXL", "^VIX", "EEM", "EDC", "TLT", "EDZ", "EMB"]
ticker_list2 = ticker_list + ["strat"]
data = None
if use == "yfinance":
    data = yf.download(ticker_list, start=period_start, end=period_end)[["Close"]]["Close"]
elif use == "polygon":
    spy = get_daily_near_closing_value(ticker="SPY")
    spxl = get_daily_near_closing_value(ticker="SPXL")
    tlt = get_daily_near_closing_value(ticker="TLT")
    eem = get_daily_near_closing_value(ticker="EEM")
    edc = get_daily_near_closing_value(ticker="EDC")
    edz = get_daily_near_closing_value(ticker="EDZ")
    vix = get_daily_near_closing_value(ticker="I:VIX")
    polygon_data = pd.concat([spy,tlt, eem, edc, vix, spxl, edz], axis=1)
    data = polygon_data
    data = data.rename(columns={"close_SPY": "SPY",
                                "close_SPXL": "SPXL",
                                "close_I:VIX": "^VIX",
                                "close_TLT": "TLT",
                                "close_EEM": "EEM",
                                "close_EDC": "EDC",
                                "close_EDZ": "EDZ",
                                })
else:
    print("Error")

# Get the day of the week, and remove the friday Close to monday close returns
print(data.head().to_string())
data["weekday"] = pd.to_datetime(data.index).weekday
data["date"] = pd.to_datetime(data.index)
data["days_skip"] = (data["date"] - data["date"].shift(1)).dt.days - 1


data["eem_strat_ret"] = risk_free_rate
data["spy_strat_ret"] = risk_free_rate
data["edc_strat_ret"] = risk_free_rate
data["edz_strat_ret"] = risk_free_rate
data["spxl_strat_ret"] = risk_free_rate



for ticker in ticker_list:
    data[f"{ticker}_ret"] = (data[ticker] - data[ticker].shift(1)) / data[ticker].shift(1)
    data[f"{ticker}_prior"] = data[ticker].shift(1)


# Now for the strategies:
# EEM and Levered EEM (EDC)
data["eem_strat_ret"][data["SPY_ret"].shift(1) < data["TLT_ret"].shift(1)] = data["EEM_ret"]
data["edc_strat_ret"][data["SPY_ret"].shift(1) < data["TLT_ret"].shift(1)] = data["EDC_ret"]
data["edz_strat_ret"][data["SPY_ret"].shift(1) > data["TLT_ret"].shift(1)] = data["EDZ_ret"]


# SPY and levered SPY (SPXL)
data["spy_strat_ret"][data["SPY_ret"].shift(1) > data["TLT_ret"].shift(1)] = data["SPY_ret"]
data["spxl_strat_ret"][data["SPY_ret"].shift(1) > data["TLT_ret"].shift(1)] = data["SPXL_ret"]


# Let's get buy+hold returns for each ETF.
etf_list = ["SPY", "EEM", "EDC", "TLT", "SPXL", "EMB"]
for ticker in etf_list:
    data[f"{ticker}_returns"] = portfolio_start * (1 + data[f"{ticker}_ret"]).cumprod()

# setting up the more complicated strategy
data["strat_eem_longonly_ret"] = risk_free_rate
data["strat_edc_longonly_ret"] = risk_free_rate
data["strat_longshort_basic_ret"] = risk_free_rate
data["strat_longshort_tlt_eem_ret"] = risk_free_rate
data["strat_levered_etf_ret"] = risk_free_rate
data["strat_longshort_emb_eem_ret"] = risk_free_rate

# EEM Long only
data["strat_eem_longonly_ret"][(data["SPY_ret"].shift(1) < data["TLT_ret"].shift(1))
                        ] = data["EEM_ret"]

# EDC Long only
data["strat_edc_longonly_ret"][(data["SPY_ret"].shift(1) < data["TLT_ret"].shift(1))
                        ] = data["EDC_ret"]

# EEM Long/Short basic.
data["strat_longshort_basic_ret"][(data["SPY_ret"].shift(1) < data["TLT_ret"].shift(1))
                        ] = data["EEM_ret"]
data["strat_longshort_basic_ret"][(data["SPY_ret"].shift(1) > data["TLT_ret"].shift(1))
                        ] = -data["EEM_ret"]

# EEM and TLT long/short
data["strat_longshort_tlt_eem_ret"][(data["SPY_ret"].shift(1) < data["TLT_ret"].shift(1))
                        ] = data["EEM_ret"] - data["TLT_ret"]
data["strat_longshort_tlt_eem_ret"][(data["SPY_ret"].shift(1) > data["TLT_ret"].shift(1))
                        ] = -data["EEM_ret"] + data["TLT_ret"]

# EMB and EEM long/short
data["strat_longshort_emb_eem_ret"][(data["SPY_ret"].shift(1) < data["TLT_ret"].shift(1))
                        ] = data["EEM_ret"] - data["EMB_ret"]
data["strat_longshort_emb_eem_ret"][(data["SPY_ret"].shift(1) > data["TLT_ret"].shift(1))
                        ] = -data["EEM_ret"] + data["EMB_ret"]

# I've noticed that EDC+SPXL trades do better when not holding over the weekend or a "skipped" market day.
data["strat_levered_etf_ret"][(data["SPY_ret"].shift(1) < data["TLT_ret"].shift(1))
                        & (data["days_skip"] == 0)
                        ] = data["EDC_ret"]
data["strat_levered_etf_ret"][(data["SPY_ret"].shift(1) > data["TLT_ret"].shift(1))
                        & (data["days_skip"] == 0)
                        ] = data["SPXL_ret"]

final_list = [
    "strat_eem_longonly","strat_edc_longonly",
    "strat_levered_etf",
    "strat_longshort_basic", "strat_longshort_tlt_eem", "strat_longshort_emb_eem",
    "EDC", "EEM", "SPY", "SPXL",
]

for ticker in final_list:
    data[f"{ticker}_returns"] = portfolio_start * (1 + data[f"{ticker}_ret"]).cumprod()
    data[f"{ticker}_drawdown"] = (data[f"{ticker}_returns"] - data[f"{ticker}_returns"].cummax()) / data[f"{ticker}_returns"].cummax()



plt.figure(dpi=150)
plt.xticks(rotation=45)
plt.suptitle(f"Returns of Buy & Hold ETFs and Basic EEM Strategy")
plt.title(f"Profit over time period") # Get the dates from X to Y as well.
legend_list = []
for ticker in ["EEM", "EMB", "SPY", "TLT", "strat_longshort_basic"]:
    temp2 =f"{ticker} Return"
    plt.plot(data.index, data[f"{ticker}_returns"], label=temp2)
    legend_list.append(temp2)
plt.legend(legend_list)
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
plt.tight_layout()
plt.yscale(yscale)
plt.show()


plt.figure(dpi=150)
plt.xticks(rotation=45)
plt.suptitle(f"Returns of Buy & Hold ETFs and Long-Only EEM Strategy")
plt.title(f"Profit over time period") # Get the dates from X to Y as well.
legend_list = []
for ticker in ["EEM", "EMB", "SPY", "TLT", "strat_eem_longonly"]:
    temp2 =f"{ticker} Return"
    plt.plot(data.index, data[f"{ticker}_returns"], label=temp2)
    legend_list.append(temp2)
plt.legend(legend_list)
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
plt.tight_layout()
plt.yscale(yscale)
plt.show()


plt.figure(dpi=150)
plt.xticks(rotation=45)
plt.suptitle(f"Returns of Buy & Hold ETFs, EEM Long Only and EDC Long Only")
plt.title(f"Profit over time period") # Get the dates from X to Y as well.
legend_list = []
for ticker in ["EEM", "SPY", "TLT", "strat_eem_longonly", "strat_edc_longonly"]:
    temp2 =f"{ticker} Return"
    plt.plot(data.index, data[f"{ticker}_returns"], label=temp2)
    legend_list.append(temp2)
plt.legend(legend_list)
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
plt.tight_layout()
plt.yscale(yscale)
plt.show()

plt.figure(dpi=150)
plt.xticks(rotation=45)
plt.suptitle(f"Compare EEM Long/Short strategy to EEM")
plt.title(f"Profit over time period") # Get the dates from X to Y as well.
legend_list = []
for ticker in ["EEM", "SPY", "strat_longshort_basic"]:
    temp2 =f"{ticker} Return"
    plt.plot(data.index, data[f"{ticker}_returns"], label=temp2)
    legend_list.append(temp2)
plt.legend(legend_list)
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
plt.tight_layout()
plt.yscale(yscale)
plt.show()

plt.figure(dpi=150)
plt.xticks(rotation=45)
plt.suptitle(f"Compare EEM+TLT Long/Short Strategy to EEM LongShort")
plt.title(f"Profit over time period") # Get the dates from X to Y as well.
legend_list = []
for ticker in ["EEM", "EMB", "SPY", "strat_longshort_basic", "strat_longshort_tlt_eem", "strat_longshort_emb_eem"]:
    temp2 =f"{ticker} Return"
    plt.plot(data.index, data[f"{ticker}_returns"], label=temp2)
    legend_list.append(temp2)
plt.legend(legend_list)
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
plt.tight_layout()
plt.yscale(yscale)
plt.show()


# Look at SPXL+EDC long-only
plt.figure(dpi=150)
plt.xticks(rotation=45)
plt.suptitle(f"Comparison EDC+SPXL strategy to other EEM strategies and Buy+Hold")
plt.title(f"Profit over time period") # Get the dates from X to Y as well.
legend_list = []
for ticker in ["strat_levered_etf", "strat_eem_longonly", "strat_edc_longonly", "EDC", "SPXL", "SPY" ]:
    temp2 =f"{ticker} Return"
    plt.plot(data.index, data[f"{ticker}_returns"], label=temp2)
    legend_list.append(temp2)
plt.legend(legend_list)
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
plt.tight_layout()
plt.yscale(yscale)
plt.show()



plt.figure(dpi=150)
plt.xticks(rotation=45)
plt.suptitle(f"Comparison of strategies together")
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


# Now, let's get some statistics on our Strategy versus 
for ticker in final_list:
    print(f"{ticker} Sharpe Ratio: ", round((data[f"{ticker}_ret"].mean() - risk_free_rate) / data[f"{ticker}_ret"].std() * np.sqrt(252),2),
    f" Sortino Ratio: ", round((data[f"{ticker}_ret"].mean() - risk_free_rate) / data[data[f"{ticker}_ret"] < 0][f"{ticker}_ret"].std() * np.sqrt(252),2),
    f" Profit Factor: ", round(data[f"{ticker}_ret"][data[f"{ticker}_ret"] > 0].sum() / abs(data[f"{ticker}_ret"][data[f"{ticker}_ret"] < 0].sum()),2),
    f" % Trades Profitable: ", round(np.where(data[f"{ticker}_ret"] > 0 ,1 ,0).mean() * 100,2),
    f" % of Period Invested: ", round(np.where(data[f"{ticker}_ret"] != risk_free_rate ,1 ,0).mean() * 100,2),
    f" Max Drawdown: ", round(data[f"{ticker}_drawdown"].min() * 100, 2),
    f" Avg Return/Day When Invested: ", round(data[f"{ticker}_ret"][data[f"{ticker}_ret"] != 0].mean() * 100,2), "%",
    f" Annual Return: ",round((100 * (((1 + data[f"{ticker}_ret"].mean()) ** 252) - 1)),2), "%",
          )
