from datetime import datetime
import pandas as pd
import pandas_ta as ta
from backtesting import Backtest, Strategy

class BuyDipSellGain(Strategy):
    def init(self):
        self.trending_symbol = None

    def next(self):
        if self.trending_symbol is None:
            # Check if symbol is trending
            sma = self.data.ta.sma(20)  # Calculate the 20-period SMA using pandas_ta
            if self.data.Close[-1] > sma[-1]:
                self.trending_symbol = True

        elif self.trending_symbol:
            sma = self.data.ta.sma(20) 
            if self.data.Close[-1] < sma[-1]:
                # Symbol has dipped below the 20-period SMA
                # Check for a green engulfing candle
                if self.data.Close[-1] > self.data.Open[-1] and self.data.Open[-2] > self.data.Close[-2]:
                    self.buy()

# Load the data
data = pd.read_csv('/Users/tc/Dropbox/dev/github/Trading-Algos-By-Moon-Dev/buy_the_dip/ETH-USD-15m-2020-09-10T23_45_00+0800.csv', parse_dates=['datetime'])
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