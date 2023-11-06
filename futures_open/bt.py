from backtesting import Backtest, Strategy
import pandas as pd

# Load data from .csv file
df = pd.read_csv('futures_open/BTC-USD-15m-2023-1-01T00_00.csv')

# Adjust column names for backtrader and capitalize first letter
df.columns = ['datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'extra']

# Drop unused 'extra' column if it exists
if 'extra' in df.columns:
    df = df.drop(columns=['extra'])

# Convert datetime column to DatetimeIndex and convert UTC to EST
df['datetime'] = pd.to_datetime(df['datetime'])
df.set_index('datetime', inplace=True)

# Define the trading strategy
class SundayEveningStrategy(Strategy):
    def init(self):
        self.buy_price = 0
    
    # In the next() method of SundayEveningStrategy
    # In the next() method of SundayEveningStrategy
    def next(self):
        time = self.data.index[-1]
        if time.weekday() == 6:  # Check if it's Sunday
            print(f"Timestamp: {time}, Hour: {time.hour}, Minute: {time.minute}")
            if time.hour == 20 and time.minute == 45:
                self.buy_price = self.data['Close'][-1]
                print("Buy condition met.")
                order = self.buy()  # get the order details
                print("Buy order details:", order)
            elif time.hour == 23 and time.minute == 45 and self.buy_price > 0:
                print("Sell condition met.")
                order = self.position.close()  # get the order details
                print("Sell order details:", order)

# Run the backtest
bt = Backtest(df, SundayEveningStrategy, cash=1000000, commission=.002)
output = bt.run()
print(output)