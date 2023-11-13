import pandas as pd
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

# Load your cryptocurrency data
data = pd.read_csv('quant_gpt/BTC-USD-6h-2020-1-01T00_00.csv')

# Convert the 'datetime' column to a datetime object and set as index
data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)

# Capitalize column names to match the expected format by backtesting.py
data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

class EMARsiStrategy(Strategy):
    def init(self):
        price = self.data.Close
        self.ema_fast = self.I(talib.EMA, price, 9)
        self.ema_slow = self.I(talib.EMA, price, 21)
        self.rsi = self.I(talib.RSI, price, 14)

    def next(self):
        if crossover(self.ema_fast, self.ema_slow) and self.rsi > 30:
            self.buy()
        elif crossover(self.ema_slow, self.ema_fast) and self.rsi < 70:
            self.sell()

# Run the backtest
bt = Backtest(data, EMARsiStrategy, cash=1000000, commission=.002)
stats = bt.run()
print(stats)
