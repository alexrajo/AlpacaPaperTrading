import alpaca_trade_api as alpaca
import alpha_vantage as alphav
import requests
import time
from datetime import datetime
from stock_retriever import *
import strategies.golden_cross

from config import *


ALPACA_ENDPOINT = "https://paper-api.alpaca.markets"
DATA_ENDPOINT = "https://www.alphavantage.co/query"
INTRADAY_PARAMS = {
    "function": "TIME_SERIES_INTRADAY",
    "symbol": "AAPL",
    "interval": "5Min",
    "adjusted": True,
    "outputsize": "full",
    "apikey": ALPHA_VANTAGE_KEY}

LATEST_PARAMS = {
    "function": "GLOBAL_QUOTE",
    "symbol": "AAPL",
    "apikey": ALPHA_VANTAGE_KEY}

stock_amount = 1
tick_interval = 300


class Trader:
    def __init__(self):
        self.api = alpaca.REST(KEY_ID, SECRET_KEY, base_url=ALPACA_ENDPOINT)
        self.account = self.api.get_account()
        self.target_stocks = []

    def fullbuy(self, symbol, stock_info):
        positions = self.api.list_positions()
        for pos in positions:
            if pos["symbol"] == symbol:
                print("Already own shares of {}".format(symbol))
                return

        buying_power = self.account.buying_power
        price = stock_info["c"]
        qty = int(buying_power/price/max(1, stock_amount-len(positions)))
        self.market_buy(symbol=symbol, qty=qty)

    def market_buy(self, symbol, qty):
        self.api.submit_order(
            symbol=symbol,
            qty=qty,
            side="buy",
            type="market",
            time_in_force="day"
        )
        print("Bought {} shares of {}".format(qty, symbol))

    def sell_all(self, symbol):
        position = self.api.get_position(symbol=symbol)
        if position is None:
            print("I don't own any shares of {}".format(symbol))
            return

        buying_power = self.account.buying_power
        portfolio = self.account.equity

        qty = position["qty"]
        self.market_sell(symbol, qty=qty)

    def market_sell(self, symbol, qty):
        self.api.submit_order(
            symbol=symbol,
            qty=qty,
            side='sell',
            type='market',
            time_in_force='day'
        )
        print("Sold {} shares of {}".format(qty, symbol))

    def clear(self):
        # positions = self.api.list_positions()
        # assets = self.api.list_assets()
        self.api.close_all_positions()


if __name__ == "__main__":
    trader = Trader()
    account = trader.account
    clock = trader.api.get_clock()

    while True:
        calcs = {}
        if not clock.is_open:
            trader.clear()

            for calc in calcs:
                del calc

            calcs = {}
            next_open = datetime.strptime(str(clock.next_open)[:-6], "%Y-%m-%d %H:%M:%S")
            now = datetime.strptime(str(clock.timestamp)[:-16], "%Y-%m-%d %H:%M:%S")
            difference = next_open - now
            seconds_to_open = difference.total_seconds()
            time.sleep(seconds_to_open)

        trader.target_stocks = get_stocks(stock_amount)

        for stock in trader.target_stocks:
            continue
            params = INTRADAY_PARAMS
            params["symbol"] = stock["symbol"]
            response = requests.get(DATA_ENDPOINT, params=params).json()
            content = response["Time Series (Daily)"]

            calc = strategies.golden_cross.Strategy()
            calcs[stock["symbol"]] = calc

            for t in content:
                bar = content[t]
                info = {
                    "t": t,
                    "o": float(bar["1. open"]),
                    "h": float(bar["2. high"]),
                    "l": float(bar["3. low"]),
                    # "c": float(bar["4. close"]),
                    "c": float(bar["5. adjusted close"]),
                    "v": int(bar["6. volume"])
                }
                calc.on_data(info=info)


        while clock.is_open:
            for stock in trader.target_stocks:
                calc = calcs[stock["symbol"]]
                if calc is None:
                    continue

                params = LATEST_PARAMS
                params["symbol"] = stock["symbol"]
                response = requests.get(DATA_ENDPOINT, params=params).json()
                print(response)
                bar = response["Global Quote"]
                info = {
                    "o": float(bar["02. open"]),
                    "h": float(bar["03. high"]),
                    "l": float(bar["04. low"]),
                    "c": float(bar["05. price"]),
                    # "ac": float(bar["5. adjusted close"]),
                    "v": int(bar["06. volume"])
                }

                decision = calc.on_data(info=info)  # 1=buy, -1=sell
                if decision == 1:

                    trader.fullbuy(symbol=stock["symbol"], stock_info=info)
                elif decision == -1:
                    trader.sell_all(symbol=stock["symbol"])

            time.sleep(tick_interval)
