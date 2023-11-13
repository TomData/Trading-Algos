# First order that will open your position
side = 1 # open long
type = 'market'
amount = 1 # your amount here

opening_order = exchange.create_order(symbol, type, side, amount)

# Second order that will reduce your position

params = {
    'reduceOnly': True
}

reduce_side = 4 # close long -> the opposite of the first order
reduce_amount = x # your reduce amount here
reduce_type = 'market'

reduce_order = exchange.create_order(symbol, reduce_type, reduce_side, reduce_amount, None, params)
