import dydx.constants as consts
from dydx.client import Client

def get_highest_and_lowest_funding_rate_symbols():
    client = Client()

    # Fetch all trading pairs available on DyDX
    trading_pairs = client.public.get_markets()

    highest_funding_rate_symbol = ""
    highest_funding_rate = float('-inf')
    lowest_funding_rate_symbol = ""
    lowest_funding_rate = float('inf')

    # Iterate over each trading pair to find the highest and lowest funding rates
    for pair in trading_pairs:
        market_id = pair['id']
        trading_pair = pair['symbol']
        funding_rates = client.public.get_funding_rates(market_id=market_id)

        for funding_rate in funding_rates:
            rate = funding_rate['rate']

            # Update highest funding rate and symbol if a new highest rate is found
            if rate > highest_funding_rate:
                highest_funding_rate = rate
                highest_funding_rate_symbol = trading_pair

            # Update lowest funding rate and symbol if a new lowest rate is found
            if rate < lowest_funding_rate:
                lowest_funding_rate = rate
                lowest_funding_rate_symbol = trading_pair

    # Output the highest and lowest funding rate symbols and rates
    print(f"Highest Funding Rate Symbol: {highest_funding_rate_symbol}, Rate: {highest_funding_rate}")
    print(f"Lowest Funding Rate Symbol: {lowest_funding_rate_symbol}, Rate: {lowest_funding_rate}")


# Call the function to retrieve and display the highest and lowest funding rates
get_highest_and_lowest_funding_rate_symbols()