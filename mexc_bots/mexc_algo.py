# api_key = 'dsfdfdsggss'
# secret = 'gsgdssdgdgs'

'''
today we are building a bot that uses the VWAP and trades on MEXC

- build for spot because mexc futures doesnt work
'''

import ccxt
import dontshareconfig as ds 
import time 

# Use your MEXC API credentials here
api_key = ds.api_key
secret_key = ds.secret

# Connect to MEXC exchange

mexc_futures = ccxt.mexc({
    'apiKey': api_key,
    'secret': secret_key,
    'options': {
        'createMarketBuyOrderRequiresPrice': False,
    },
})

# gets price 
symbol = 'LINKUSDT'
#balance = float(mexc_futures.fetch_balance()["USDT"]["free"]) - float(mexc_futures.fetch_balance()["USDT"]["free"])/100*5
price = float(mexc_futures.fetch_ticker(symbol)["last"])
leverage = 0
print(f'price of {symbol}: {price}')

# set leverage
# params = {'openType': 1,  'positionType':1}
# leverage = 2
# mexc_futures.set_leverage(leverage, symbol, params)

# open an order
# First order that will open your position
side = 1 # open long 1= long 0 = short
type = 'market'
amount = 1 # your amount here

opening_order = mexc_futures.create_order(symbol, type, side, amount)
