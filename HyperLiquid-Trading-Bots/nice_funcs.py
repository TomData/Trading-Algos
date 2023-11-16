#key = 'klhjklhjklhjklhjk' -- this is whats in the dontshareconfig.py

'''
building a bot to trade new altcoins on hyperliquid 
pip install hyperliquid-python-sdk

only way to get access to hyperliquid and 
save huge on fees: https://app.hyperliquid.xyz/join/MOONDEV 

Success
- we can now get bid/ask, change leverage, and make orders

RBI 
R - researching different strategies
B - backtest those strategies
I - implement to bots, small size 30 days, scale if good

ex - https://github.com/hyperliquid-dex/hyperliquid-python-sdk 
docs- https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint 
examples - https://github.com/hyperliquid-dex/hyperliquid-python-sdk/tree/master/examples 


todo -
- figure out how to round price per symbol
- cancel only symbols order, one at at atime
- get data from HL
'''

from dontshareconfig import key  
#key = 'klhjklhjklhjklhjk' -- this is whats in the dontshareconfig.py (private key, keep safe af)

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
timeframe = '15m'
limit = 1000 
max_loss = -1
target = 5
pos_size = 200
leverage = 10
vol_multiplier = 3
rounding = 4

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
    rounding = get_sz_px_decimals(coin)[0]
    sz = round(sz,rounding)
    # limit_px = round(limit_px,rounding)
    print(f'placing limit order for {coin} {sz} @ {limit_px}')
    order_result = exchange.order(coin, is_buy, sz, limit_px, {"limit": {"tif": "Gtc"}}, reduce_only=reduce_only)

    if is_buy == True:
        print(f"limit BUY order placed thanks moon, resting: {order_result['response']['data']['statuses'][0]}")
    else:
        print(f"limit SELL order placed thanks moon, resting: {order_result['response']['data']['statuses'][0]}")

    return order_result

def get_sz_px_decimals(symbol):

    '''
    this is succesfully returns Size decimals and Price decimals

    this outputs the size decimals for a given symbol
    which is - the SIZE you can buy or sell at
    ex. if sz decimal == 1 then you can buy/sell 1.4
    if sz decimal == 2 then you can buy/sell 1.45
    if sz decimal == 3 then you can buy/sell 1.456

    if size isnt right, we get this error. to avoid it use the sz decimal func
    {'error': 'Invalid order size'}
    '''
    url = 'https://api.hyperliquid.xyz/info'
    headers = {'Content-Type': 'application/json'}
    data = {'type': 'meta'}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        # Success
        data = response.json()
        #print(data)
        symbols = data['universe']
        symbol_info = next((s for s in symbols if s['name'] == symbol), None)
        if symbol_info:
            sz_decimals = symbol_info['szDecimals']
            
        else:
            print('Symbol not found')
    else:
        # Error
        print('Error:', response.status_code)

    ask = ask_bid(symbol)[0]
    #print(f'this is the ask {ask}')

    # Compute the number of decimal points in the ask price
    ask_str = str(ask)
    if '.' in ask_str:
        px_decimals = len(ask_str.split('.')[1])
    else:
        px_decimals = 0

    print(f'{symbol} this is the price {sz_decimals} decimal(s)')

    return sz_decimals, px_decimals


def adjust_leverage(symbol, leverage):
    account = LocalAccount = eth_account.Account.from_key(key)
    exchange = Exchange(account, constants.MAINNET_API_URL)
    info = Info(constants.MAINNET_API_URL, skip_ws=True)

    print('leverage:', leverage)

    exchange.update_leverage(leverage, symbol)

def get_ohclv(cb_symbol, timeframe, limit):

    coinbase = ccxt.kraken()

    ohlcv = coinbase.fetch_ohlcv(cb_symbol, timeframe, limit)
    #print(ohlcv)

    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    df = df.tail(limit)

    df['support'] = df[:-2]['close'].min()
    df['resis'] = df[:-2]['close'].max()

    # Save the dataframe to a CSV file
    df.to_csv('ohlcv_data.csv', index=False)

    return df 


def supply_demand_zones(symbol, timeframe, limit):

    print('starting moons supply and demand zone calculations..')

    sd_df = pd.DataFrame()

    df = get_ohclv(cb_symbol, timeframe, limit)
    #print(df)

    supp = df.iloc[-1]['support']
    resis = df.iloc[-1]['resis']
    #print(f'this is moons support for 1h {supp_1h} this is resis: {resis_1h}')

    df['supp_lo'] = df[:-2]['low'].min()
    supp_lo = df.iloc[-1]['supp_lo']

    df['res_hi'] = df[:-2]['high'].max()
    res_hi = df.iloc[-1]['res_hi']

    sd_df[f'{timeframe}_dz'] = [supp_lo, supp]
    sd_df[f'{timeframe}_sz'] = [res_hi, resis]

    print('here are moons supply and demand zones')
    print(sd_df)

    return sd_df 


def get_position(symbol):

    '''
    gets the current position info, like size etc. 
    '''

    account = LocalAccount = eth_account.Account.from_key(key)
    info = Info(constants.MAINNET_API_URL, skip_ws=True)
    user_state = info.user_state(account.address)
    print(f'this is current account value: {user_state["marginSummary"]["accountValue"]}')
    positions = []
    for position in user_state["assetPositions"]:
        if (position["position"]["coin"] == symbol) and float(position["position"]["szi"]) != 0:
            positions.append(position["position"])
            in_pos = True 
            size = float(position["position"]["szi"])
            pos_sym = position["position"]["coin"]
            entry_px = float(position["position"]["entryPx"])
            pnl_perc = float(position["position"]["returnOnEquity"])*100
            print(f'this is the pnl perc {pnl_perc}')
            break 
    else:
        in_pos = False 
        size = 0 
        pos_sym = None 
        entry_px = 0 
        pnl_perc = 0

    if size > 0:
        long = True 
    elif size < 0:
        long = False 
    else:
        long = None 

    return positions, in_pos, size, pos_sym, entry_px, pnl_perc, long 


def cancel_all_orders():
    # this cancels all open orders
    account = LocalAccount = eth_account.Account.from_key(key)
    exchange = Exchange(account, constants.MAINNET_API_URL)
    info = Info(constants.MAINNET_API_URL, skip_ws=True)

    open_orders = info.open_orders(account.address)
    #print(open_orders)

    print('above are the open orders... need to cancel any...')
    for open_order in open_orders:
        #print(f'cancelling order {open_order}')
        exchange.cancel(open_order['coin'], open_order['oid'])

def volume_spike(df):
    # A volume spike would be significantly larger than the current moving average of volume
    df['MA_Volume'] = df['volume'].rolling(window=20).mean()

    # A downward trend can be seen when the current close price is below the moving average of close price
    df['MA_Close'] = df['close'].rolling(window=20).mean()
    # print(df['MA_Volume'])
    # print(df['MA_Close'])

    latest_data = df.iloc[-1]
    volume_spike_and_price_downtrend = latest_data['volume'] > vol_multiplier * latest_data['MA_Volume'] and latest_data['MA_Close'] > latest_data['close']

    return volume_spike_and_price_downtrend

def kill_switch(symbol):

    positions, im_in_pos, pos_size, pos_sym, entry_px, pnl_perc, long = get_position(symbol)

    while im_in_pos == True:

        cancel_all_orders()

        # get bid_ask
        askbid = ask_bid(pos_sym)
        ask = askbid[0]
        bid = askbid[1]

        pos_size = abs(pos_size)

        if long == True:
            limit_order(pos_sym, False, pos_size, ask)
            print('kill switch - SELL TO CLOSE SUBMITTED ')
            time.sleep(5)
        elif long == False:
            limit_order(pos_sym, True, pos_size, bid)
            print('kill switch - BUY TO CLOSE SUBMITTED ')
            time.sleep(5)
        
        positions, im_in_pos, pos_size, pos_sym, entry_px, pnl_perc, long = get_position(symbol)

    print('position successfully closed in kill switch')

def pnl_close(symbol):

    print('entering pnl close')
    positions, im_in_pos, pos_size, pos_sym, entry_px, pnl_perc, long = get_position(symbol)

    if pnl_perc > target:
        print(f'pnl gain is {pnl_perc} and target is {target}... closing position WIN')
        kill_switch(pos_sym)
    elif pnl_perc <= max_loss:
        print(f'pnl loss is {pnl_perc} and max loss is {max_loss}... closing position LOSS')
        kill_switch(pos_sym)
    else:
        print(f'pnl loss is {pnl_perc} and max loss is {max_loss} and target {target}... not closing position')
    print('finished with pnl close')

# pnl_close()

# # df = get_ohclv(cb_symbol, timeframe, limit)
# # print(volume_spike(df))
# # time.sleep(876)

# #kill_switch(symbol)

# cancel_all_orders()
# askbid = ask_bid(symbol)
# bid = askbid[1]
# ask = askbid[0]
# l2_data = askbid[2]
# #print(l2_data)

# #limit_order(symbol, True, pos_size, bid) # buy order
# #limit_order(symbol, False, pos_size, ask) # sell order

# time.sleep(7)

