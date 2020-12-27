# pycoin

PyCoin is an automated cryptocurrency trading application. Right now it is just a pet project, but will hopefully become more than that soon. It consists of two parts – intermarket arbitrage, and intramarket arbitrage. Both are very much a work in progress.

## Intramarket

An automated speed trading algorithm for cryprocurrency using LSTM. Cryptocurrency was chosen over the stock market due to the limits on trading frequency with less than $25K in your portfolio. The goal of this algorithm is to predict with a >51% gain or loss on bitcoin within the second and then make a trade based on that data.

### Trading Logic

The trading logic used for this is based on the derivative of the predictions graph. Currently the algorithm is able to correctly predict whether the crypto price is increasing or decreasing no less than 80% of the time. I have found the model to perform best with the lookback set to `1`, epochs between `10` and `15`, and units around `256`. I also found that the size of the rolling dataset works best between `1800` to `2400` datapoints. According to graph error, it looks as though the model needs to be retrained every half an hour to an hour at minimum. As far as structure goes – the main class will be `CryptoTrader`. It will incorporate `CrytoPredictor` and `KrakenTrader` and bring them together in one class for a fully functioned release.

### Sample Output (w/ small dataset)
```
$ python3 CryptoTrader.py

********************************************************************************
* WARNING: DATASET LENGTH < 1800 (actual = 29)
* MODEL PERFORMANCE WILL BE SUBOPTIMAL
********************************************************************************

Dataset loaded into frame in 0.00s
Loaded model from disk
Last model trained at 2020-12-27 11:53:02.864641-05:00

--------------------------------------------------------------------------------
@ 12/27/2020 11:53:27
--------------------------------------------------------------------------------
n-1: $26709.60 (actual)
n: $26701.80 (actual)

n-1: $26722.85 (predicted)
n: $26699.83 (predicted)
n+1: $26719.16 (predicted)

actual (previous) d/dx: -0.78

predicted (previous) d/dx: -2.30
predicted (next) d/dx: 1.93

predicted action: buy
-------------------------------------------------------------------------------- 

+ Balance:
  + 0.00 USD
  + 0.01872533 BTC
   (bought)

* Using 399.57 MB of memory

Last model trained at 2020-12-27 11:53:02.864641-05:00
+ Recieved response with ['Ticker', 'pair=xxbtzusd'] - [1609088018.161651, '26718.40000', '26706.40000', '26706.50000', '10654.96793825', '27264.32520', 59483, '26245.90000', '28353.20000', '2']
+ Saved response at time 2020-12-27 11:53:38.161651-05:00 to file data/xbt-usd_kraken.csv

********************************************************************************
* WARNING: DATASET LENGTH < 1800 (actual = 30)
* MODEL PERFORMANCE WILL BE SUBOPTIMAL
********************************************************************************

Dataset loaded into frame in 0.00s
Loaded model from disk

--------------------------------------------------------------------------------
@ 12/27/2020 11:53:39
--------------------------------------------------------------------------------
n-1: $26701.80 (actual)
n: $26718.40 (actual)

n-1: $26699.83 (predicted)
n: $26719.16 (predicted)
n+1: $26713.58 (predicted)

actual (previous) d/dx: 1.66

predicted (previous) d/dx: 1.93
predicted (next) d/dx: -0.56

predicted action: sell
-------------------------------------------------------------------------------- 

+ Balance:
  + 500.31 USD
  + 0.00000000 BTC
   (sold)

* Using 407.32 MB of memory
```

### Charts
Note that these are just samples from my tests and may not be the direct result of the ouptput immediately above.<br>
Historical hourly Bitcoin prices –
![Hourly prices](chart/hourly_prices.png)
Historical prices + predicted with actual prices –
![Predictions](chart/predictions.png)
Historical prices + predicted with actual prices (zoomed in) –
![Zoomed Predictions](chart/predictions_zoomed.png)
Rate of change of predicted prices –
![Slope](chart/slope.png)
Perent error in rate of change of predicted prices –
![Error](chart/error.png)

<!-- 
## Intermarket

This side of pycoin will scan given markets for each's crypto price, make a decision on the greatest difference between the two, buy at the lowest, and sell at the highest – all with in the same moment.

Example call for prices: 
```
Asking for BTC on binanceusa...
Asking for BTC on bittrex...
Asking for BTC on kraken...
Asking for BTC on bitfinex...
Asking for BTC on bitstamp...
Asking for BTC on gemini...
At 2020-12-11 10:19:47.768476
{
  "binanceusa": 18058.85,
  "bittrex": 18073.28,
  "kraken": 18070.1,
  "bitfinex": 18087.0,
  "bitstamp": 18070.29,
  "gemini": 18074.83
}
Lowest = binanceusa at $18058.85
Highest = bitfinex at $18087.0
Gross difference => $28.15

Testing ROI per transaction
-----------------------------
Net ROI w/ $10 invested => $0.0255
Net ROI w/ $20 invested => $0.0511
Net ROI w/ $30 invested => $0.0766
Net ROI w/ $40 invested => $0.1021
Net ROI w/ $50 invested => $0.1276
Net ROI w/ $60 invested => $0.1532
Net ROI w/ $70 invested => $0.1787
Net ROI w/ $80 invested => $0.2042
Net ROI w/ $90 invested => $0.2298
Net ROI w/ $100 invested => $0.2553
...Net ROI w/ $500 invested => $1.2764
...Net ROI w/ $1000 invested => $2.5528
...Net ROI w/ $3000 invested => $7.6585
...Net ROI w/ $9000 invested => $22.9754
```

Keep in mind this is meant to be traded up to every 10 seconds, so these values compounded == $$$. Or, at least $.
-->