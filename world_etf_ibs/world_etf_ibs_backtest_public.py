"""
This is a general backtest.
You can alter the:
1. Factors
2. Start/Stop day period
3. Holding period
4. Slippage
5. Number of stocks charted
6. ETF list

IBS is (Close - Low)/(High - Low)

"""

import pandas as pd
import yfinance as yf
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")


start_date = "2013-01-01"
end_date = "2026-01-01"
holding_period = "Gap" # Can be "Gap", "Intraday", or "1 Day"
slippage = 0#0.0005#0.0001 #0.01%? or 0.05% of slippage? What's a good amount?
stock_num = 5 # how many top/bottom stocks are we going to check metrics for at the end.

# Get every country ETF I can find:
# Using Global/iShares MSCI Country ETFs
etf_list = [
    "SPY", # United States
    "ARGT", # Argentina
    "COLO", # Columbia
    "GREK", # Greece
    "NORW", # Norway
    "VNAM", # Vietnam
    "EWA", # Australia
    "EWO", # Austria
    "EWK", # Belgium
    "EWC", # Canada
    "ECH", # Chile
    "MCHI", # China
    "EDEN", # Denmark
    "EFNL", # Finland
    "EWQ", # France
    "EWG", # Germany
    "EWH", # Hong Kong
    "INDA", # India
    "EIDO", # Indonesia
    "EIRL", # Ireland
    "EIS", # Israel
    "EWI", # Italy
    "EWJ", # Japan
    "KWT", # Kuwait
    "EWM", # Malaysia
    "EWW", # Mexico
    "EWN", # Netherlands
    "ENZL", # New Zealand
    "EPU", # Peru (and Global exposure?)
    "EPHE", # Philippines
    "EPOL", # Poland
    "QAT", # Qatar
    "KSA", # Saudi Arabia
    "EWS", # Singapore
    "EZA", # South Africa
    "EWY", # South Korea
    "EWP", # Spain
    "EWD", # Sweden
    "EWL", # Switzerland
    "EWT", # Taiwan
    "THD", # Thailand
    "TUR", # Turkey
    "UAE", # UAE
    "EWU", # United Kingdom
    "EWZ", # Brazil
    # These weren't obvious ETFS. Have Low volume or... other reasons why they're not easy to find.
    "ERUS", # Russia ?!?
    "PGAL", # Portugal
    "NGE", # Nigeria
    "PAK", # Pakistan ?!? They're weird.
    "EGPT", # Egypt? but it's VanEck, not MSCI
    "GLCR", # Iceland, but it's not MSCI
]

# What if we used only the 18 Country ETFs + SPY that we started with in ~1998?
#etf_list = ['SPY', 'EWH', 'EWU', 'EWN', 'EWI', 'EWP', 'EWO', 'EWA', 'EWK', 'EWD', 'EWM', 'EWJ', 'EWC', 'EWW', 'EWL', 'EWG', 'EWQ', 'EWS']

# Metals Oil+Nat Gas, Agriculture-related ETFs are interesting.
#etf_list = ["SPY", "PALL", "PPLT", "GLD", "UX", "CPER", "SLV", "BNO", "UGA", "UNG", "UNL", "USO", "USL", "CANE", "CORN", "SOYB", "WEAT"]

# What About in-US sector ETFs? Sorta work
#etf_list = ["SPY","XLC", "XLY", "XLP", "XLE", "XLF", "XLV", "XLI", "XLB", "XLRE", "XLK", "XLU"]

# What about Futures? They also can be done, but Futures are scary.  (CL=F in 2020 went negative).
# I'm also not sure if yahoo finance's "close" prices are calculated at the same time between assets like stocks are.
etf_list = ["ES=F", "ZB=F", "GC=F", "CL=F", "NG=F", "RB=F", "HG=F", "SI=F", "NQ=F", "ZN=F", "HO=F", "ZC=F", "ZS=F", "HE=F", "LE=F", "CT=F", "SB=F"]

# Industry specific ETFs? Also works on 1 Day timeframe.
#etf_list = ["SPY", "ITA", "IYM", "IAI", "IYC", "IEDI", "IYK", "IDGT", "IYE", "IYG", "IYF", "IYH", "IHF", "ITB", "IYJ", "IAK", "IHI", "IEO", "IEZ", "IHE", "IYR", "IAT", "IYW", "IYZ", "IYT", "IDU"]


print(etf_list)
ref_etf = etf_list[0]
df = []
for ticker in etf_list:
    temp = yf.download(ticker, start=start_date, end=end_date)
    temp.columns = temp.columns.droplevel(1)
    temp["ticker"] = ticker
    # Return Stuff:
    if holding_period == "1 Day":
        temp["return"] = (temp["Close"] - temp["Close"].shift(1))/temp["Close"].shift(1)# 1 Day Return
    elif holding_period == "Gap":
        temp["return"] = (temp["Open"] - temp["Close"].shift(1)) / temp["Close"].shift(1) # Gap Return
    elif holding_period == "Intraday":
        temp["return"] = (temp["Close"] - temp["Open"]) / temp["Open"] # IntraDay Return

    temp["return_next"] = temp["return"].shift(-1)
    temp["return_previous"] = temp["return"].shift(1)

    # Metrics
    temp["ibs"] = (temp["Close"] - temp["Low"]) / (temp["High"] - temp["Low"])
    temp["notional_volume"] = (temp["Close"] * temp["Volume"])
    temp["price_effect"] = np.log(temp["Close"])
    temp["mean_reversion"] = abs(temp["Close"] - temp["Close"].rolling(10).mean()) / temp["Close"].rolling(10).mean()
    # Time stuff
    temp["date"] = temp.index.astype(str)
    temp["month"] = temp.index.month
    temp["year"] = temp.index.year
    temp["day"] = temp.index.day
    temp["day_name"] = temp.index.day_name()

    df.append(temp)
    print(ticker, "done")
    print(ticker, "fist trade at:", temp["date"].min(), "last trade at:", temp["date"].max())



# merge them all together
df = pd.concat(df, axis=0)

# get our reference ETF:
ref = df[df["ticker"] == ref_etf]

df["factor"] = df["ibs"] # actually works okay for the gap...
df["factor2"] = df["mean_reversion"]


# What if we want to make sure we're only trading ETFs with a threshold notional volume?
# We need actual volume to make a trade. $100000 in trading volume for the day should be a good threshold.
# increasing the threshold will decrease the returns, but that's probably just the price for scale.
df = df[df["notional_volume"] > 100000]
# want High > Low (need some movement in stock)
df = df[df["High"] > df["Low"]]

# Now make a factor that we'll rank:
df = df.sort_values(by=["date", "factor", "factor2"], ascending=[True, False, True])
df["factor_rank"] = df.groupby("date")["factor"].cumcount() + 1
# And ranked the other way, to get Top and Bottom assets by number.
df = df.sort_values(by=["date", "factor", "factor2"], ascending=[True, True, False])
df["factor_rankr"] = df.groupby("date")["factor"].cumcount() + 1

# True "rank" of Returns (1 is high+, 45 is low-, for instance)
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
# It looks like getting the Top/Bottom 1 ETF is the optimal target.
plt.figure()
plt.xticks(rotation=45)
plt.suptitle(f"Top {stock_num} Ranked Stocks Daily Performance")
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
print("Profit Factor", np.where(temp["return_next"] > 0, temp["return_next"], 0).sum() / (
            -1 * np.where(temp["return_next"] < 0, temp["return_next"], 0).sum()))

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
    print(f"{len(list(set(temp["ticker"])))} Tickers Used:", list(set(temp["ticker"])))

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
    print(f"{len(list(set(temp["ticker"])))} Tickers Used:", list(set(temp["ticker"])))


# Let's see if there's anything weird in this data:
temp = df[df["factor_rankr"] == 1]
#print(temp[["ticker", "date", "return", "return_next", "Open", "High", "Low", "Close", "ibs", "mean_reversion"]].to_string())
# Let's take a look at the "True Rank" Value counts:
# We want factor_rankr == true_rankr, but how often do we get there.
print("What is the distribution of the actual Rank for returns for the top-predicted ETFs each day?")
print(temp["true_rank"].value_counts(sort=True, ascending=False, dropna=True))

# Now let's visualize how the algorithm sorts it
count_matrix = pd.crosstab(index=df['factor_rankr'], columns=df['true_rank'])
plt.figure(figsize=(8, 6)) # Optional: Adjust figure size
sns.heatmap(count_matrix, annot=False, fmt='d', cmap='viridis')

# Add labels and title for clarity
plt.title('Crosstab Heatmap of Predicted Rank vs True Rank')
plt.xlabel('True Rank')
plt.ylabel('Factor Rank')
plt.show()


# Arithmatic Monthly Returns, as a heatmap
monthly_returns_matrix = ref.pivot_table(values=f'return_next', index="year", columns="month")

# Set the column names to the month names
monthly_returns_matrix.columns = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
# Calculate the sum of monthly returns for each year
yearly_returns = ref.groupby(ref.index.year)[f'return_next'].sum()
# Add the yearly returns to the matrix as a new column
monthly_returns_matrix['Yearly'] = yearly_returns

# Set the font scale
sns.set(font_scale=0.5)
# Plot the heatmap using seaborn
plt.figure(dpi=120)
sns.heatmap(monthly_returns_matrix, annot=True, cmap='RdYlGn', center=0, fmt='.1%', cbar=False)
plt.title(f'{ref_etf} Normal Monthly and Yearly Aritmatic Returns by Year and Month', fontsize=10)
plt.xlabel('Month', fontsize=8)
plt.ylabel('Year', fontsize=8)
plt.show()
sns.set(font_scale=1.0)


# Let's do it for Temp = factor_rank == 1
temp = df[df["factor_rank"] == 1]
monthly_returns_matrix = temp.pivot_table(values="return_next", index="year", columns="month")

# Set the column names to the month names
monthly_returns_matrix.columns = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
# Calculate the sum of monthly returns for each year
yearly_returns = temp.groupby(temp.index.year)[f'return_next'].sum()
# Add the yearly returns to the matrix as a new column
monthly_returns_matrix['Yearly'] = yearly_returns

# Set the font scale
sns.set(font_scale=0.5)
# Plot the heatmap using seaborn
plt.figure(dpi=120)
sns.heatmap(monthly_returns_matrix, annot=True, cmap='RdYlGn', center=0, fmt='.1%', cbar=False)
plt.title(f'Top IBS Strategy Monthly and Yearly Arithmatic Returns by Year and Month', fontsize=10)
plt.xlabel('Month', fontsize=8)
plt.ylabel('Year', fontsize=8)
plt.show()
sns.set(font_scale=1.0)


# Let's do it for Temp = factor_rankr == 1
temp = df[df["factor_rankr"] == 1]
monthly_returns_matrix = temp.pivot_table(values="return_next", index="year", columns="month")

# Set the column names to the month names
monthly_returns_matrix.columns = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
# Calculate the sum of monthly returns for each year
yearly_returns = temp.groupby(temp.index.year)[f'return_next'].sum()
# Add the yearly returns to the matrix as a new column
monthly_returns_matrix['Yearly'] = yearly_returns

# Set the font scale
sns.set(font_scale=0.5)
# Plot the heatmap using seaborn
plt.figure(dpi=120)
sns.heatmap(monthly_returns_matrix, annot=True, cmap='RdYlGn', center=0, fmt='.1%', cbar=False)
plt.title(f'Bottom IBS Strategy Monthly and Yearly Arithmatic Returns by Year and Month', fontsize=10)
plt.xlabel('Month', fontsize=8)
plt.ylabel('Year', fontsize=8)
plt.show()
sns.set(font_scale=1.0)


# print the Bottom thingy.
temp = df[df["factor_rankr"] == 1]
#print(temp.head().to_string())
# Let's take a look at Avg, Median Daily returns for each stock, see if there's a horrible one.
# We also want to make sure that Russia wasn't included after like... 2022-06-01?
temp = temp.groupby("ticker").agg(avg_return=("return_next", "mean"),
                                  med_return=("return_next", "median"),
                                  days_traded=("date", "nunique"),
                                  avg_true_rank=("true_rankr", "mean"),
                                  med_true_rank=("true_rankr", "median"))
print(temp.sort_values(by="avg_return", ascending=False).to_string())

