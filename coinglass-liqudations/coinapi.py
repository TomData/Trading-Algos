from coinglass_api import CoinglassAPI
from dontshareconfig import coinglass_api

cg = CoinglassAPI(coinglass_secret=coinglass_api)

# Get perpetual markets for BTC
perp_markets_btc = cg.perpetual_market(symbol="BTC")

print(perp_markets_btc)