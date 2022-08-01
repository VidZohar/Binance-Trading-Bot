# Binance-Trading-Bot
Crypto Trading Bot for the Binance Testnet

Programmed my own BNB/USDT trading algorithm that automatically makes trades based on the formula I created. 

It uses 1 minute candlesticks and calculates average price, EMA, SMA. Based on these parameters and 42 previous price points, it calculates if it's appropriate to open a buy or sell position on BNB/USDT pair. 

Use of websocket connection and Binance testnet. 

Comments: 
- Should take longer candlesticks (30 minutes - 2 hours) to more accurately predict parameters. 
- Using 1 minute candlesticks leads to too many trades - trading fees become a problem.
- Should upgrade my trading formula, reconsider weights of parameters and take into consideration more historical price points. 
