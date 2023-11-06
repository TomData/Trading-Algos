'''
pass the time interval eg. m1 m5 m15 m30 h1 h4 ...
minutes and hours we can pass in 
'''

import pandas as pd
from coinglass_api import CoinglassAPI
from dontshareconfig import coinglass_api

# Initialize API
cg = CoinglassAPI(coinglass_secret=coinglass_api)

# Set your time interval here
time_interval = "h1" # m1 m5 m15 m30 h1 h4 ...

# Get liquidation data for BTC
liq_btc = cg.liquidation_symbol(symbol="ETH", interval=time_interval)

# Convert data to pandas DataFrame
df = pd.DataFrame(liq_btc)

# Export data to CSV file
df.to_csv('coinglass-liqudations/coinglass-liquidations.csv', index=False)

# Calculate and print sums
sum_volUsd = df['volUsd'].sum()
sum_sellVolUsd = df['sellVolUsd'].sum()
sum_buyVolUsd = df['buyVolUsd'].sum()
sum_turnoverNumber = df['turnoverNumber'].sum()
sum_buyTurnoverNumber = df['buyTurnoverNumber'].sum()
sum_sellTurnoverNumber = df['sellTurnoverNumber'].sum()

print("Data has been written to coinglass-liquidations.csv in the current directory")

print("Sum of volUsd: ${:,.2f}".format(sum_volUsd))
print("Sum of sellVolUsd: ${:,.2f}".format(sum_sellVolUsd))
print("Sum of buyVolUsd: ${:,.2f}".format(sum_buyVolUsd))
print("Sum of turnoverNumber: ${:,.2f}".format(sum_turnoverNumber))
print("Sum of buyTurnoverNumber: ${:,.2f}".format(sum_buyTurnoverNumber))
print("Sum of sellTurnoverNumber: ${:,.2f}".format(sum_sellTurnoverNumber))