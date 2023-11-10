import discord
from discord.ext import commands, tasks
import donstshareconfig as d
import requests
import pandas as pd
import datetime

bot_token = d.discord_token
channel_id = int(d.channel_id)

# Create an instance of the bot
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
bot = commands.Bot(command_prefix='!', intents=intents)

df = None

def get_most_common_coins(hours):
    global df
    window_start = datetime.datetime.now() - datetime.timedelta(hours=hours)
    window_end = datetime.datetime.now()
    window_df = df[(df['date'] >= window_start.strftime("%m-%d-%y %I:%M %p")) 
                   & (df['date'] <= window_end.strftime("%m-%d-%y %I:%M %p"))]
    if window_df.empty:
        return None
    most_common_coins = window_df['coin'].value_counts().head(7)  # get top 7 coins
    return most_common_coins

@tasks.loop(seconds=60*15)  # runs every 15 minutes
async def run_bot():
    global df
    response = requests.get('https://api.coingecko.com/api/v3/search/trending?vs_currency=usd&order=market_cap_desc&per_page=250&page=1&sparkline=false')

    try:
        df = pd.read_csv('lowcapgem_algo/coingecko.csv')
    except:
        df = pd.DataFrame()

    now = datetime.datetime.now().strftime("%m-%d-%y %I:%M %p")

    for coin in response.json()['coins']:
        coinname = coin['item']['name']
        rank = coin['item']['market_cap_rank']
        temp_df = pd.DataFrame({
            'date': [now],
            'coin': [coinname],
            'rank': [rank]
        })
        df = pd.concat([df, temp_df])

    df = df.iloc[::-1]
    df.to_csv('lowcapgem_algo/coingecko.csv', index=False)
    channel = bot.get_channel(channel_id)

    trending_24h = get_most_common_coins(24)
    trending_72h = get_most_common_coins(72)

    if trending_24h is not None:
        msg = "Most Trending Coins in the Last 24 Hours:\n"
        for coin, count in trending_24h.items():
            rank = df[df['coin'] == coin]['rank'].values[0]
            msg += f"{coin}: Count {count}, Rank {rank}\n"
    else:
        msg = "No Trending Coins in the Last 24 Hours."
    await channel.send('```' + msg + '```')

    if trending_72h is not None:
        msg_72 = "Most Trending Coins in the Last 72 Hours:\n"
        for coin, count in trending_72h.items():
            rank = df[df['coin'] == coin]['rank'].values[0]
            msg_72 += f"{coin}: Count {count}, Rank {rank}\n"
    else:
        msg_72 = "No Trending Coins in the Last 72 Hours."
    await channel.send('```' + msg_72 + '```')

@bot.event
async def on_ready():
    print('Bot started.')
    run_bot.start()  # start the loop

bot.run(bot_token)