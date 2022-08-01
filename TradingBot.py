import pandas as pd
import numpy as np
from binance.client import Client
from binance.enums import *
import websocket, json, pprint
from ta.trend import EMAIndicator, SMAIndicator
import config

SOCKET = 'wss://stream.binance.com:9443/ws/bnbusdt@kline_1m'    # possible timeframes: 1m, 3m, 5m, 15m, 30m, 1h, 2h,...

client = Client(config.BINANCE_API_KEY, config.BINANCE_SECRET_KEY)

# for testing:
client.API_URL = 'https://testnet.binance.vision/api'

TRADE_SYMBOL = 'BNBUSDT'
TRADE_QUANTITY = 0.1

average_prices = []
in_position = False

# FUNCTION FOR CREATING ORDER (OPENING POSITION)
def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        #print('Sending order')          
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        return False
    return True

def on_open(ws):
    print('Opened connection')

def on_close(ws):
    print('Closed connection')

def on_message(ws, message):
    global average_prices
    global in_position
    print('Received message')
    json_message = json.loads(message)
    #pprint.pprint(json_message)

    candle = json_message['k']
    is_candle_closed = candle['x']  # if 'x' = True, candle is closed/finished

    high = float(candle['h'])
    low = float(candle['l'])
    close = float(candle['c'])     

    average_price = (high + low + close) / 3

    if is_candle_closed:
        average_prices.append(average_price)
        df = pd.DataFrame(average_prices, columns=['average_price'])
        #print(df['average_price'].iloc[-5:])            # pusti vse stolpce, ampak daj v else stavek na koncu

        if len(average_prices) > 42:                         
            ap_ema_ind = EMAIndicator(df['average_price'], 10)       
            df['ap_ema'] = ap_ema_ind.ema_indicator()
            df['difference'] = np.abs(df['average_price'] - df['ap_ema'])  
            diff = EMAIndicator(df['difference'], 10)                        
            df['diff_ema'] = diff.ema_indicator()        
            df['ci'] = (df['average_price'] - df['ap_ema']) / (0.015 * df['diff_ema'])
            ci_ema = EMAIndicator(df['ci'], 21)      
            df['wt1'] = ci_ema.ema_indicator()
            wt1_sma = SMAIndicator(df['wt1'], 4)  
            df['wt2'] = wt1_sma.sma_indicator()

            print(df)  
            print(client.get_asset_balance(asset='BNB'))  
            print(client.get_asset_balance(asset='USDT'))  
            
            if df.iloc[-2, -1] > df.iloc[-2, -2]:       # wt2[-2] > wt1[-2]
                if df.iloc[-1, -1] < df.iloc[-1, -2]:   # wt2[-1] < wt1[-1]
                    if not in_position:                                    
                        print('BUY')
                        order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                        in_position = True
                        print(client.get_asset_balance(asset='BNB'))  
                    else:
                        print('Already in position')
                else:
                    exit
            elif df.iloc[-2, -1] < df.iloc[-2, -2]:     # wt2[-2] < wt1[-2]
                if df.iloc[-1, -1] > df.iloc[-1, -2]:   # wt2[-1] > wt1[-1]
                    if in_position:
                        print('SELL')
                        order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                        in_position = False
                        print(client.get_asset_balance(asset='BNB')) 
                    else:
                        print('Not in position')
                else:
                    exit       
        else:
            print(df['average_price']) 

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
