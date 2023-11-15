#key = 'klhjklhjklhjklhjk'

'''
building a bot to trade new altcoins on hyperliquid 
pip install hyperliquid-python-sdk
* fixed bug by changing enviroment to 3.8.5

Success
- we can now get bid/ask, change leverage, and make orders

RBI 
R - researching different strategies
B - backtest those strategies
I - implement to bots, small size 30 days, scale if good

todo -
- pos info 
'''

from dontshareconfig import key 
from eth_account.signers.local import LocalAccount
import eth_account
import json
import time 
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants
import ccxt
import pandas as pd
import datetime
import schedule 
import requests 

symbol = 'SOL' 
timeframe = '1m'
limit = 100 
max_loss = -2
target = 5
pos_size = 1
leverage = 10

cb_symbol = symbol + '/USDT' #BTC/USD

def ask_bid(symbol):

    url = 'https://api.hyperliquid.xyz/info'
    headers = {'Content-Type': 'application/json'}

    data = {
        'type': 'l2Book',
        'coin': symbol
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    l2_data = response.json()
    l2_data = l2_data['levels']
    #print(l2_data)

    # get bid and ask 
    bid = float(l2_data[0][0]['px'])
    ask = float(l2_data[1][0]['px'])

    return ask, bid, l2_data

def limit_order(coin: str, is_buy: bool, sz: float, limit_px: float, reduce_only: bool = False):
    account: LocalAccount = eth_account.Account.from_key(key)
    exchange = Exchange(account, constants.MAINNET_API_URL)
    sz = round(sz,1)
    limit_px = round(limit_px,2)
    print(f'placing limit order for {coin} {sz} @ {limit_px}')
    order_result = exchange.order(coin, is_buy, sz, limit_px, {"limit": {"tif": "Gtc"}}, reduce_only=reduce_only)

    if is_buy == True:
        print(f"limit BUY order placed, resting: {order_result['response']['data']['statuses'][0]}")
    else:
        print(f"limit SELL order placed, resting: {order_result['response']['data']['statuses'][0]}")

    return order_result

def adjust_leverage(symbol):
    account = LocalAccount = eth_account.Account.from_key(key)
    exchange = Exchange(account, constants.MAINNET_API_URL)
    info = Info(constants.MAINNET_API_URL, skip_ws=True)

    print('leverage:', leverage)

    exchange.update_leverage(leverage, symbol)

def get_ohclv(cb_symbol, timeframe, limit):

    coinbase = ccxt.binance()

    ohlcv = coinbase.fetch_ohlcv(cb_symbol, timeframe, limit)
    print(ohlcv)

    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    df = df.tail(limit)

    df['support'] = df[:-2]['close'].min()
    df['resis'] = df[:-2]['close'].max()

    return df 


print(get_ohclv(cb_symbol, '1h', 1000))

askbid = ask_bid(symbol)
bid = askbid[1]
ask = askbid[0]
l2_data = askbid[2]
print(l2_data)

#limit_order(symbol, True, pos_size, bid) # buy order
#limit_order(symbol, False, pos_size, ask) # sell order