from datetime import datetime
import pandas as pd
from backtesting import Backtest, Strategy

class BuyDipSellGain(Strategy):
    buy_threshold = 0  # Define buy_threshold as a class variable
    take_profit = 0  # Define take_profit as a class variable
    stop_loss = 0  # Define stop_loss as a class variable

    def init(self):
        self.buy_price = 0

    def next(self):
        if self.buy_threshold is not None and \
                self.take_profit is not None and \
                self.stop_loss is not None:
            
            equity_high = max(self.data.High)
            max_dip = (self.data.Close[-1] - equity_high) / equity_high

            if max_dip <= self.buy_threshold and self.buy_price == 0:
                self.buy_price = self.data.Close[-1]

            if self.buy_price > 0:
                take_profit_price = self.buy_price * self.take_profit
                stop_loss_price = self.buy_price * self.stop_loss

                if self.data.Close[-1] >= take_profit_price or \
                        self.data.Close[-1] <= stop_loss_price:
                    self.position.close()
                    self.buy_price = 0

# Load the data
data = pd.read_csv('/Users/tc/Dropbox/dev/github/Trading-Algos-By-Moon-Dev/buy_the_dip/ETH-USD-1d-2015-1-02T00:00.csv', parse_dates=['datetime'])
data.set_index('datetime', inplace=True)
data.columns = [column.capitalize() for column in data.columns]

# Create an instance of the backtest with the strategy
bt = Backtest(data, BuyDipSellGain, cash=10000, commission=0.0005)

# Optimize the buy threshold, take profit, and stop loss
optimization_results = bt.optimize(
    buy_threshold=[i / 100 for i in range(2, 5)],
    take_profit=[1 + (i / 100) for i in range(2, 5)],
    stop_loss=[1 - (i / 100) for i in range(2, 5)],
    maximize='Equity Final [$]'
)

# Print the optimization results
print(optimization_results)

# Run the backtest with the selected parameters
buy_threshold = optimization_results.loc[0, 'buy_threshold']
take_profit = optimization_results.loc[0, 'take_profit']
stop_loss = optimization_results.loc[0, 'stop_loss']
bt = Backtest(data, BuyDipSellGain, cash=10000, commission=0.0005)
results = bt.run(buy_threshold=buy_threshold, take_profit=take_profit, stop_loss=stop_loss)

# Print the performance metrics
print(results)

# Plot the performance
bt.plot()