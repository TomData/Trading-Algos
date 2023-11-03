# Funding Rate Arbitrage

overview-
we are looking long one asset and short the other. we will short the Super high funding rate asset, and then long the super low funding rate. 

things to test
1. is it better to long the negative funding and short the positive, or the other way around. 

notes
1. may be hard to backtest cause we need all historical funding data. 

resources: 
https://www.luxeeai.com//dydx-funding-rate-arbitrage-discrepancies

https://www.luxeeai.com//building-funding-rate-arbitrage-algorithm-dydx-backtesting-approach 

Todo list
0. try to backtest this idea with grabbing historical funding rates
1. build out a script that gets the highest and lowest funding rate symbols -- use dydx functions we already have. 
2. double check there is enough volume in the two symbols
2.5. build some rules to enter only when > x funding rate or < y funding rate. 
3. build bot that buys one and sells the other