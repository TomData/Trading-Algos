# demand zone volume spike bot

overview -
we are going to build a backtest for a demand zone algo that buys the demand zones but only after a large volume spike of on the 15 min chart. the demand zones are going to be between the last lowest low and lowest close in the last 30 bars. the buy will be placed .2% lower than the demand zone, but only with there was a volume spike of 2x or more in the current bar or in the past 5 bars. use a take profit of 1.5% and stop of 1.5%

here is a sample of the data and the location: demand_zone_vol/ETH-USD-15m-2023-1-01T00_00.csv
datetime, open, high, low, close, volume,
2023-01-01 00:00:00, 1195.25, 1196, 1193.6, 1193.8, 1882.90305929,
2023-01-01 00:15:00, 1193.77, 1195.95, 1193.42, 1195.72, 3036.86051892,
2023-01-01 00:30:00, 1195.72, 1195.72, 1191.87, 1192.84, 3162.96159989,
2023-01-01 00:45:00, 1192.75, 1194.57, 1192.61, 1193.35, 1531.08853562,
2023-01-01 01:00:00, 1193.32, 1195.14, 1193.02, 1194.69, 1694.38366579,
2023-01-01 01:15:00, 1194.71, 1195.01, 1194.17, 1194.74, 1092.39434233,
2023-01-01 01:30:00, 1194.79, 1194.89, 1193.76, 1194.14, 1017.94491185,

use the optmizer to test different values for the volume spike (test 2-7x spike) optimize for how much lower than the demand zone we should buy (test .1-.9%) then also optimize for the different amount of bars in the past to look for the volume spike (test 1-5 bars) 

resources: www.luxeeai.com/building-backtest-demand-zone-algorithm 

tests 
- test the 5 min chart 
- test the volume spike amount of 2-5x
- test different demand zone calculations
- test different amount of bars for the volume in past 