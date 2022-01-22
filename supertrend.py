import ccxt
import schedule
import pandas as pd
import requests
pd.set_option('display.max_rows', None)

import warnings
warnings.filterwarnings('ignore')

import numpy as np
from datetime import datetime
import time

# Discord information
url = "https://discord.com/api/webhooks/934498898188316733/ZIMG3EtBM0zUCKnPobmfh_Xl_RxDIDY1Er1kMjwU901L6P3AQsmhcQV16Llpn_ITkK0U"

#Exchange you're using to scrape data
exchange = ccxt.bybit({})

# SuperTrend stuff
def tr(data):
    data['previous_close'] = data['close'].shift(1)
    data['high-low'] = abs(data['high'] - data['low'])
    data['high-pc'] = abs(data['high'] - data['previous_close'])
    data['low-pc'] = abs(data['low'] - data['previous_close'])

    tr = data[['high-low', 'high-pc', 'low-pc']].max(axis=1)

    return tr

def atr(data, period):
    data['tr'] = tr(data)
    atr = data['tr'].rolling(period).mean()

    return atr

def supertrend(df, period=7, atr_multiplier=3):
    hl2 = (df['high'] + df['low']) / 2
    df['atr'] = atr(df, period)
    df['upperband'] = hl2 + (atr_multiplier * df['atr'])
    df['lowerband'] = hl2 - (atr_multiplier * df['atr'])
    df['in_uptrend'] = True

    for current in range(1, len(df.index)):
        previous = current - 1

        if df['close'][current] > df['upperband'][previous]:
            df['in_uptrend'][current] = True
        elif df['close'][current] < df['lowerband'][previous]:
            df['in_uptrend'][current] = False
        else:
            df['in_uptrend'][current] = df['in_uptrend'][previous]

            if df['in_uptrend'][current] and df['lowerband'][current] < df['lowerband'][previous]:
                df['lowerband'][current] = df['lowerband'][previous]

            if not df['in_uptrend'][current] and df['upperband'][current] > df['upperband'][previous]:
                df['upperband'][current] = df['upperband'][previous]
        
    return df


in_position = False

def check_buy_sell_signals(df):
    global in_position

    print("\033[1;31;40m \n\nchecking for buy and sell signals \n \033")
    print(df.tail(5))
    last_row_index = len(df.index) - 1
    previous_row_index = last_row_index - 1

    if not df['in_uptrend'][previous_row_index] and df['in_uptrend'][last_row_index]:
        print("\033[1;32;40m changed to uptrend, alerted in Discord! \033") # Prints alert to console
        data = {
    "content" : "BNB/USDT 15m\nBNB changed to uptrend, buy!",
    "username" : "Super Signals"
    }
        requests.post(url, json = data) # Send messsage to Discord webhook

    
    if df['in_uptrend'][previous_row_index] and not df['in_uptrend'][last_row_index]:
            print("\033[1;31;40m changed to downtrend, sell \033") # Prints alert to console 
            data = {
                "content" : "BNB/USDT 15m\nBNB changed to downtrend, sell!",
                "username" : "Super Signals"
            }
            requests.post(url, json = data) # Send messsage to Discord webhook
def run_bot():
    print(f"Fetching new bars for {datetime.now().isoformat()}")
    bars = exchange.fetch_ohlcv('BNB/USDT', timeframe='15m', limit=100) # Defines currency you want to use and some other shit

    df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    supertrend_data = supertrend(df)
    
    check_buy_sell_signals(supertrend_data)


schedule.every(15).minutes.do(run_bot)


while True:
    schedule.run_pending()
    time.sleep(1)
