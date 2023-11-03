import dydx.constants as consts
from dydx.client import Client
from datetime import datetime
from backtesting import Strategy, Backtest
from backtesting.lib import crossover

class FundingRateArbitrage(Strategy):
    def init(self):
        self.client = Client()
        self.highest_funding_rate_symbol = ""
        self.lowest_funding_rate_symbol = ""
        self.long_position_entry = False
        self.pnl_target = 0.005 # 0.5%
        self.loss_threshold = -0.005 # -0.5%

    def on_start(self):
        self.fetch_highest_and_lowest_funding_rate_symbols()

    def fetch_highest_and_lowest_funding_rate_symbols(self):
        trading_pairs = self.client.public.get_markets()

        highest_funding_rate = float('-inf')
        lowest_funding_rate = float('inf')

        for pair in trading_pairs:
            market_id = pair['id']
            trading_pair = pair['symbol']
            funding_rates = self.client.public.get_funding_rates(market_id=market_id)

            for funding_rate in funding_rates:
                rate = funding_rate['rate']

                if rate > highest_funding_rate:
                    highest_funding_rate = rate
                    self.highest_funding_rate_symbol = trading_pair

                if rate < lowest_funding_rate:
                    lowest_funding_rate = rate
                    self.lowest_funding_rate_symbol = trading_pair

    def next(self):
        if self.data.datetime[-1].hour % 8 == 0:  # Execute every 8 hours
            current_funding_rate = self.client.public.get_funding_rates(self.data._name)[0]['rate']
            annualized_funding_rate = current_funding_rate * 3 * 365  # Assuming 3 funding periods per day
            pnl = 0

            if self.long_position_entry:
                if not crossover(self.data.Open, self.data.Close):
                    self.position.close()
                    pnl = (self.data.Close[0] - self.position.entry_price) / self.position.entry_price

            if annualized_funding_rate > 0.9:
                self.position.close()
                self.position = self.enter_short()
                self.long_position_entry = False
            elif self.lowest_funding_rate_symbol != "" and not self.long_position_entry:
                self.position.close()
                self.position = self.enter_long()
                self.long_position_entry = True

            if pnl < self.loss_threshold:
                self.position.close()

            # Output the current date, funding rates, and positions
            print(f"Date: {self.data.datetime[-1]}")
            print(f"Highest Funding Rate: {self.highest_funding_rate_symbol}, Rate: {annualized_funding_rate}")
            print(f"Lowest Funding Rate: {self.lowest_funding_rate_symbol}")
            print(f"Position: {self.position}")

# Set the desired trading pair for backtesting
trading_pair = "ETH-USDC"

# Fetch historical data for the specified trading pair
client = Client()
data = client.public.get_historical_index_prices(market_id=consts.MARKET_IDS[trading_pair])

# Create and run the backtest using the FundingRateArbitrage strategy
bt = Backtest(data, FundingRateArbitrage, cash=10000, commission=0.0005)
results = bt.run()

# Print the equity curve and statistics
print(results.equity_curve)
print(results.stats)