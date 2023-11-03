# Buy the dip

overview
build me a backtest using backtesting.py that buys ethereum whenever there is a 20% dip from the high and then sells back after 10% gain

https://www.luxeeai.com//backtesting-strategy-ethereum-20-percent-dip-10-percent-gain 

https://www.luxeeai.com//backtesting-strategy-buying-ethereum-on-20-percent-dips-and-selling-on-10-percent-gains 

todo 
1. set up backtest, and optimize for dip value + tp/sl
2. build out algo if prof

Different buy the dips to backtest-
1. 15 min dip buyer, that buys like the example.png
    find a tredning 15 min symbol
    wait til it dips under the 15min 20sma
    then wait for a Green engulfing, then enter long. 
    backtest this, test diff tps & sls
https://www.luxeeai.com//trending-symbol-dip-buying-strategy-python-backtesting

2. on the daily timeframe (test diff timeframes)
    buy the dip of (5-30%) and then simply hold for 8 bars (test 4-20 bars) no stop loss or tp, simply close when the # of bars are hit.
https://www.luxeeai.com//buy-dip-strategy-hold-x-bars-daily-timeframe
