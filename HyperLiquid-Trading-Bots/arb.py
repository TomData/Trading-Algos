import nice_funcs as n 
import time, schedule 

# building an arb bot based off the funding rates
# lower funding rate, long, higher funding rate, short 

sym1 = 'BTC'
sym2 = 'ETH'
usdsize = 150 
lev = 10 
target = .6
max_loss = -.9

def size_for_both():

    # do math to get size for both
    sym1askbid = n.ask_bid(sym1)
    s1bid = sym1askbid[1]
    sym2askbid = n.ask_bid(sym2)
    s2bid = sym2askbid[1]

    s1sz = ( usdsize / s1bid ) * lev
    s2sz = (usdsize /s2bid) * lev

    s1dec = n.get_sz_px_decimals(sym1)[0]
    s2dec = n.get_sz_px_decimals(sym2)[0]

    s1sz = round(s1sz, s1dec) 
    s2sz = round(s2sz, s2dec)

    # set lev
    n.adjust_leverage(sym1, lev)
    n.adjust_leverage(sym2, lev)

    return s1sz, s2sz

# print(size_for_both())
# time.sleep(89789)

# get prices for btc and eth 
sym1askbid = n.ask_bid(sym1)
s1bid = sym1askbid[1]
sym2askbid = n.ask_bid(sym2)
s2bid = sym2askbid[1]

# get supply and demand zones for both
# we buy the one closer to the supply and sell one close to demand
# sym1_sdz = n.supply_demand_zones(sym1, '15m', 100)
# sym2_sdz = n.supply_demand_zones(sym2, '15m', 100)

def bid_to_zones_distance(sym_bid, sym_sdz):
    dz_distance = min(abs(sym_bid - dz) / dz for dz in sym_sdz['15m_dz'])
    sz_distance = min(abs(sym_bid - sz) / sz for sz in sym_sdz['15m_sz'])
    return dz_distance, sz_distance

def closest_to_zones(sym1_bid, sym2_bid, sym1_sdz, sym2_sdz):
    sym1_dz_dist, sym1_sz_dist = bid_to_zones_distance(sym1_bid, sym1_sdz)
    sym2_dz_dist, sym2_sz_dist = bid_to_zones_distance(sym2_bid, sym2_sdz)
    
    closest_to_dz = sym1 if sym1_dz_dist < sym2_dz_dist else sym2
    closest_to_sz = sym1 if sym1_sz_dist < sym2_sz_dist else sym2

    return closest_to_dz, closest_to_sz


# # Use the new functions with the data you have
# closest_to_dz, closest_to_sz = closest_to_zones(s1bid, s2bid, sym1_sdz, sym2_sdz)
# print(f"Symbol closest to dz (demand zone) is: {closest_to_dz}")
# print(f"Symbol closest to sz (supply zone) is: {closest_to_sz}")

def bot():

    positions1, im_in_pos1, pos_size1, pos_sym1, entry_px1, pnl_perc1, long1 = n.get_position(sym1)
    positions2, im_in_pos2, pos_size2, pos_sym2, entry_px2, pnl_perc2, long2 = n.get_position(sym2)
    total_pnl = (pnl_perc1 + pnl_perc2)

    if total_pnl > target:
        print(f'total pnl: {total_pnl}% -- CLOSING as a win')
        n.kill_switch(sym1)
        n.kill_switch(sym2)
    elif total_pnl < max_loss:
        print(f'total pnl: {total_pnl}% -- CLOSING as a loss')
        n.kill_switch(sym1)
        n.kill_switch(sym2)
    else:
        print(f'total pnl: {total_pnl}%')


# TODO - make it so it checks each position and has elif if only one
# side is filled, vs if both sides, etc. 
# check to make sure in both positions or none
    if not im_in_pos1 and not im_in_pos2:

        sz1, sz2 = size_for_both()
        print('not in position so making an order for BOTH... ')
        n.cancel_all_orders()

        s1ask, s1bid, s1l2_data = n.ask_bid(sym1)
        s2ask, s2bid, s2l2_data = n.ask_bid(sym2)

        n.limit_order(sym1, True, sz1, s1bid, False)
        n.limit_order(sym2,False, sz2, s2ask, False)

    elif not im_in_pos1:

        sz1, sz2 = size_for_both()
        print(f'not in position so making an order for {sym1}... ')
        n.cancel_all_orders()

        s1ask, s1bid, s1l2_data = n.ask_bid(sym1)

        n.limit_order(sym1, True, sz1, s1bid, False)

    elif not im_in_pos2:

        sz1, sz2 = size_for_both()
        print(f'not in position so making an order for {sym2}... ')
        n.cancel_all_orders()

        s2ask, s2bid, s2l2_data = n.ask_bid(sym2)

        n.limit_order(sym2,False, sz2, s2ask, False)



bot()
schedule.every(10).seconds.do(bot)   


while True:
    try:
        schedule.run_pending()
    except:
        print('+++++ maybe an internet problem.. code failed. sleeping 10')
        time.sleep(10)