import backtesting
from backtesting import Backtest, Strategy
import pandas as pd

class DemandZoneStrategy(Strategy):
    def __init__(self):
        super().__init__()

    def init(self):
        # Calculate demand zone and volume spike conditions
        self.demand_zone = (
            (self.data.Low == self.data.Low.rolling(30).min()) &
            (self.data.Close == self.data.Close.rolling(30).min())
        )
        self.volume_spike = (
            (self.data.Volume > (self.data.Volume.rolling(5).mean() * 2)) |
            (self.data.Volume.shift() > (self.data.Volume.rolling(5).mean() * 2))
        )

    def next(self):
        buy_lower_pct = 0.002  # 0.2% lower than the demand zone
        stop_loss_pct = 0.015  # 1.5% stop loss
        take_profit_pct = 0.015  # 1.5% take profit

        if (
            self.demand_zone[-1] and
            self.volume_spike[-1] and
            self.position.is_empty() and
            self.data.Low[-1] < self.data.Close[-1]  # Additional condition to ensure buying below the demand zone
        ):
            buy_price = self.data.Low[-1] * (1 - buy_lower_pct)  # Buy lower than the demand zone
            self.buy(sl=buy_price * (1 - stop_loss_pct), tp=buy_price * (1 + take_profit_pct))

# Load and prepare data
data = pd.read_csv("demand_zone_vol/ETH-USD-15m-2023-1-01T00_00.csv")
data["datetime"] = pd.to_datetime(data["datetime"])
data = data.set_index("datetime")

# Create a new strategy instance
demand_zone_strategy = DemandZoneStrategy()

# Initialize and run the backtest
bt = Backtest(data, demand_zone_strategy, cash=10000, commission=0, exclusive_orders=False)
bt.run()

# Optimize strategy parameters
results = bt.optimize(
    buy_lower_pct=(0.001, 0.009),  # Range for buy_lower_pct parameter
    volume_spike_bars=(1, 5),  # Range for volume_spike_bars parameter
    volume_spike_multiplier=(2, 7),  # Range for volume_spike_multiplier parameter
)

# Analyze and generate performance report
print(results)