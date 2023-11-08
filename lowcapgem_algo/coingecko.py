
import requests,json, time 
import pandas as pd
import datetime 

def get_market_cap(symbol):
    url = f"https://api.coingecko.com/api/v3/coins/{symbol}"
    response = requests.get(url)
    data = response.json()
    print(data)
    market_cap = data["market_data"]["market_cap"]["usd"]
    return market_cap

# get the exchanges for each id
def get_exchange(symbol):
    url = f"https://api.coingecko.com/api/v3/coins/{symbol}/tickers"
    response = requests.get(url)
    data = response.json()
    #print(data)
    # loop through and get all exchanges
    exchanges = []
    for ticker in data["tickers"]:
        exchanges.append(ticker["market"]["name"])
        # put the exchanges into a df
        df = pd.DataFrame(exchanges)
        df.columns = ["exchange"]

    return exchanges, df

# get the trending symbol, not coin name
def get_trending():
    url = "https://api.coingecko.com/api/v3/search/trending"
    response = requests.get(url)
    data = response.json()
    #print(data)
    trending = []
    for coin in data["coins"]:
        trending.append(coin["item"]["id"])
        # get the market cap
        market_cap = get_market_cap(coin["item"]["id"])
        # get the date
        now = datetime.datetime.now().date()
        # get the rank
        rank = coin["item"]["market_cap_rank"]
        # make a df - date, symbol, rank, market cap, then all of the exhanges like this exchange, exchange, exchange etc.
        # use a temp df to return the data so i can later append it to the main df
        temp_df = pd.DataFrame()
        temp_df["date"] = [now]
        temp_df["symbol"] = [coin["item"]["id"]]
        temp_df["rank"] = [rank]
        temp_df["market_cap"] = [market_cap]
        
    print(temp_df)
    return temp_df

'''
pull the trending coins from the api, then get the below info and put in temp_df
date, symbol, rank, market cap, volume, exchange, exchange, exchange, exchange, the rest of exchanges
run every 10 minutes and append temp_df to the main df
output as a csv file
'''
def bot():
    response = requests.get('https://api.coingecko.com/api/v3/search/trending?vs_currency=usd&order=market_cap_desc&per_page=250&page=1&sparkline=false')

    #df = pd.DataFrame() # run this line the first time to create the df
    df = pd.read_csv('lowcapgem_algo/coingecko.csv') # run this line after the first time to read the df
    
    now = datetime.datetime.now().date()

    for coin in response.json()['coins']:

        print(coin)
        time.sleep(7867)
        
        coinname = coin['item']['name']
        rank = coin['item']['market_cap_rank']

        temp_df = pd.DataFrame({
            'date': [now],
            'coin': [coinname],
            'rank': [rank]
        })

        df = pd.concat([df, temp_df])

    df.to_csv('lowcapgem_algo/coingecko.csv', index=False)

    time.sleep(2)

bot()

import schedule
schedule.every(3600).seconds.do(bot)

while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except:
        print("error - probably internet, sleeping for 10 seconds")
        time.sleep(10)