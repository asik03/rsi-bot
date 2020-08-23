import websocket, json, pprint, talib
import numpy as np
from binance.client import Client
from binance.enums import *

import config

SYMBOL = "ethusdt"
INTERVAL = "1m"

# "A single connection to stream.binance.com is only valid for 24 hours; expect to be disconnected at the 24 hour mark"
# SOCKET = "wss://stream.binance.com:9443/ws/<symbol>@keyline_<interval>"
SOCKET = "wss://stream.binance.com:9443/ws/" + SYMBOL + "@kline_" + INTERVAL
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = "ETHUSD"
TRADE_QUANTITY = ""

closes = []
in_position = False

client = Client(config.API_KEY, config.API_SECRET, tld=config.BINANCE_COUNTRY)

def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        print("Sending order")
        order = client.create_order(
            symbol=symbol,
            side=side,
            type=order_type,
            quantity=quantity)
        print(order)
    except Exception as e:
        return False
    return True

def on_open(ws):
    print("Opened connection")


def on_close(ws):
    print("Closed connection")


def on_message(ws, message):
    global closes
    global in_position

    print("Received message!")
    json_message = json.loads(message)
    pprint.pprint(json_message)
    print(json_message)

    candle = json_message["k"]
    is_candle_closed = candle["x"]
    close = float(candle["c"])

    if is_candle_closed:
        print("Candle closed at {}".format(close))
        closes.append(close)
        print("closes")
        print(closes)

        if len(closes) > RSI_PERIOD:
            closes_array = np.array(closes)
            rsi = talib.RSI(closes_array, RSI_PERIOD)
            print("all rsi calculated:")
            print(rsi)
            last_rsi = rsi[-1]
            print("The current RSI is {}".format(last_rsi))

            # TODO: remake the strategies
            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print("Overbought! SELL, SELL, SELL!!")
                    #TODO: put binance sell order here
                    order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = False
                else:
                    print("It is overbought, but we don't own any. Nothing to do")
            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("It is oversold, but you already own it, nothing to do")
                else:
                    print("Oversold! BUY, BUY, BUY!!")
                    # TODO: put binance buy order logic here
                    order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_QUANTITY)


ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()


