import requests
from bs4 import BeautifulSoup as bs


PAGE_URL = "https://finance.yahoo.com/most-active"


def get_stocks(amount):
    req = requests.get(PAGE_URL)
    soup = bs(req.text, "html.parser")
    rows = soup.find(id="fin-scr-res-table").contents[1].contents[0].table.tbody.contents

    stocks = []

    for i in range(amount):
        row = rows[i]
        cols = row.contents

        info = {
            "symbol": cols[0].a.text,
            "name": cols[1].text
        }

        stocks.append(info)

    return stocks
