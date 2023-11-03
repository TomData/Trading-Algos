from datetime import datetime
import pandas as pd
from backtesting import Backtest, Strategy

class BuyDipSellGain(Strategy):
    def init(self):
        self.buy_dip = False
        self.bars_to_hold = 0
        self.bar_counter = 0

    def next(self):
        if not self.buy_dip:
            # Check for a dip
            dip_percentage = (self.data.Close[-1] - self.data.Low[-1]) / self.data.Low[-1]
            if dip_percentage >= 0.05 and dip_percentage <= 0.3:
                self.buy()
                self.buy_dip = True
                self.bars_to_hold = 8  # Adjust the number of bars to hold as desired

        elif self.buy_dip:
            self.bar_counter += 1
            if self.bar_counter >= self.bars_to_hold:
                self.position.close()
                self.buy_dip = False
                self.bar_counter = 0

# Load the data
data = pd.read_csv('/Users/tc/Dropbox/dev/github/Trading-Algos-By-Moon-Dev/buy_the_dip/ETH-USD-1d-2015-1-02T00:00.csv', parse_dates=['datetime'])
data.set_index('datetime', inplace=True)
data.columns = [column.capitalize() for column in data.columns]

# Create an instance of the backtest with the strategy
bt = Backtest(data, BuyDipSellGain, cash=10000, commission=0.0005)

# Run the backtest
results = bt.run()

# Print the performance metrics
print(results)

# Plot the performance
bt.plot()