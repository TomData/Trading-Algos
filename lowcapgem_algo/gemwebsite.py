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

    df.to_csv('lowcapgem_algo/coingecko.csv', index=False)

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

    return table_style + '''
    <h1>Trending Altcoins</h1>
    <h2>These are all the trending coins on Coingecko, refreshed every 15 minutes and stored so you dont miss any</h2>
    <table>''' + df.to_html(classes='data', header=True, index=False).replace('<td>', '<td class="date-time-col">') + '</table>'

if __name__ == '__main__':
    bot()
    # Run the bot first time before the schedule
    schedule.every(900).seconds.do(bot)
    # Start the schedule on a background thread
    t = threading.Thread(target=run_schedule)
    t.start()
    # run the flask app
    app.run(port=5000)