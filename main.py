import alpaca_trade_api as alpaca
import time
from datetime import datetime
from stock_retriever import *
from stock_analyzation import *

from config import *


ENDPOINT = "https://paper-api.alpaca.markets"
stock_amount = 5
tick_interval = 300


class Trader:
    def __init__(self):
        self.api = alpaca.REST(KEY_ID, SECRET_KEY, base_url=ENDPOINT)
        self.account = self.api.get_account()
        self.target_stocks = []

    def market_buy(self, symbol, qty):
        self.api.submit_order(
            symbol=symbol,
            qty=qty,
            side="buy",
            type="market",
            time_in_force="gtc"
        )

    def sell(self, symbol, qty, price):
        self.api.submit_order(
            symbol=symbol,
            qty=qty,
            side='sell',
            type='limit',
            time_in_force='opg',
            limit_price=price
        )


if __name__ == "__main__":
    trader = Trader()
    account = trader.account
    clock = trader.api.get_clock()

    while True:
        if not clock.is_open:
            next_open = datetime.strptime(str(clock.next_open)[:-6], "%Y-%m-%d %H:%M:%S")
            now = datetime.strptime(str(clock.timestamp)[:-16], "%Y-%m-%d %H:%M:%S")
            difference = next_open - now
            seconds_to_open = difference.total_seconds()
            time.sleep(seconds_to_open)

        trader.target_stocks = get_stocks(stock_amount)

        while clock.is_open:
            for stock in trader.target_stocks:
                decision = analyze(stock["symbol"])

            time.sleep(tick_interval)
