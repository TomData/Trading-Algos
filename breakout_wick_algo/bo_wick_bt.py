import pandas as pd
from backtesting import Backtest, Strategy

# Define your WickBreakoutStrategy class here
class WickBreakoutStrategy(Strategy):
    def init(self):
        self.watch_bars = 3  # Number of bars to watch for wicks
        
    def next(self):
        # Check for a breakout
        if self.data.Close[-1] > self.data.High[-2]:
            # Watch the specified number of bars for wicks
            wick_count = 0
            for i in range(self.watch_bars):
                if self.data.Low[-i-1] < self.data.Low[-i-2] and self.data.Low[-i-1] < self.data.Low[-i]:
                    wick_count += 1
            # Try to buy at open of the 4th to 10th bar if wicks were found
            if wick_count > 0:
                for j in range(4, 11):
                    self.buy(price=self.data.Open[-j], tp=self.data.Open[-j]*1.03, sl=self.data.Open[-j]*0.97)

# Load the data
data = pd.read_csv('breakout_wick_algo/ETH-USD-15m-2018-1-02T00:00.csv', parse_dates=['time'])

# Convert the 'time' column to datetime index
data.set_index('time', inplace=True)

data.columns = [column.capitalize() for column in data.columns]


# Create an instance of the backtest with the strategy
bt = Backtest(data, WickBreakoutStrategy, cash=100000, commission=0.002)

# Optimize the number of bars to watch for wicks, take profit, and stop loss
optimization_results = bt.optimize(
    watch_bars=range(1, 11),  # Test number of bars from 1 to 10
    take_profit=[1.02, 1.03, 1.04],  # Test different take profit levels
    stop_loss=[0.97, 0.98, 0.99],  # Test different stop loss levels
    maximize='Equity Final [$]'
)

# Print the optimization results
print(optimization_results)

# Run the backtest and get the results
results = bt.run()

# Print the performance metrics
print(results)

# Plot the performance
bt.plot()