import datetime
import time
import pandas as pd
import requests
from flask import Flask, render_template
import schedule
import threading

app = Flask(__name__)
df = None

def bot():
    global df
    print("Running bot...")
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

    # Reverse the dataframe to have the newest data on top
    df = df.iloc[::-1]

    df.to_csv('lowcapgem_algo/coingecko.csv', index=False)

def get_most_common_coins(hours):
    window_start = datetime.datetime.now() - datetime.timedelta(hours=hours)
    window_end = datetime.datetime.now()

    window_df = df[(df['date'] >= window_start.strftime("%m-%d-%y %I:%M %p")) & (df['date'] <= window_end.strftime("%m-%d-%y %I:%M %p"))]

    if window_df.empty:
        return None

    most_common_coins = window_df['coin'].value_counts().head(3)

    return most_common_coins

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route('/')
def home():
    global df
    
    table_style = '''
    <style>
        table {
            font-family: Arial, sans-serif;
            border-collapse: collapse;
            width: 100%;
        }

        th, td {
            border: 1px solid #dddddd;
            text-align: left;
            padding: 8px;
        }

        th {
            background-color: #f2f2f2;
        }

        h1 {
            text-align: center;
            font-size: 24px;
            margin-top: 20px;
        }

        h2 {
            text-align: center;
            font-size: 18px;
            margin-bottom: 20px;
        }

        .date-time-col {
            width: 120px;
        }
    </style>
    '''

    most_common_coins_24 = get_most_common_coins(24)
    most_common_coins_48 = get_most_common_coins(48)
    most_common_coins_72 = get_most_common_coins(72)

    most_common_table_24 = '''
    <h2>Most Trending Coins in the Last 24 Hours:</h2>
    <table>
      <tr>
        
        <th>Coin</th>
        <th>Count</th>
        <th>Rank</th>
        
      </tr>
    '''

    if most_common_coins_24 is not None:
        for coin, count in most_common_coins_24.items():
            rank = df[df['coin'] == coin]['rank'].values[0]
            most_common_table_24 += f'''
              <tr>
                
                <td>{coin}</td>
                <td>{count}</td>
                <td>{rank}</td>
                
              </tr>
            '''
    else:
        most_common_table_24 += '''
            <tr>
                <td colspan="3">No data available</td>
            </tr>
        '''

    most_common_table_24 += '''
        </table>
    '''

    most_common_table_72 = '''
    <h2>Most Trending Coins in the Last 72 Hours:</h2>
    <table>
      <tr>
        
        <th>Coin</th>
        <th>Count</th>
        <th>Rank</th>
        
      </tr>
    '''

    if most_common_coins_72 is not None:
        for coin, count in most_common_coins_72.items():
            rank = df[df['coin'] == coin]['rank'].values[0]
            most_common_table_72 += f'''
              <tr>
                
                <td>{coin}</td>
                <td>{count}</td>
                <td>{rank}</td>
                
              </tr>
            '''
    else:
        most_common_table_72 += '''
            <tr>
                <td colspan="3">No data available</td>
            </tr>
        '''

    most_common_table_72 += '''
        </table>
    '''

    return table_style + '''
    <h1>Trending Altcoins</h1>
    <h2>These are all the trending coins on Coingecko, refreshed every 15 minutes and stored so you don't miss any</h2>
    ''' + most_common_table_24 + '''<br>''' + most_common_table_72 + '''
    <h2>Trending Coins Data:</h2>
    <table>''' + df.to_html(classes='data', header=True, index=False).replace('<td>', '<td class="date-time-col">') + '</table>'

bot()
# Run the bot first time before the schedule
schedule.every(900).seconds.do(bot)
# Start the schedule on a background thread
t = threading.Thread(target=run_schedule)
t.start()
# run the flask app
app.run(port=5000)