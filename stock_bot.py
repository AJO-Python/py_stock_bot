# -*-coding: UTF-8-*-
import tkinter as tk
#import pandas as pd
import numpy as np
import json
import os
import requests
import datetime
from iexfinance.stocks import Stock
import random
#########################
"""
Stock name: str

Price (current): float
    Stock.get_price()
    
Price (historical): np.array([float...])
    Stock.get_historical_prices()
    Can process for N day running averages? 
    
Price trend:
    Calculate based on price_historical?
    
Book value:
    Is this the quote price from the stocks book?
    stock.get_book() -> format to get quote price
    
Value-to-Price:
    Calculate based on book_value and price_current?
    
Buy ratings:
    
Strong buys:

Dividend percent:
    
Operating Margin:
Trading Volumes:
Price-to-Earnings:
"""
#########################

def activate_sandbox_mode():
    # Using the sandbox gives randomised data but gives unlimited requests for testing purposes
    IEX_API_VERSION = "iexcloud-sandbox"
    os.environ["IEX_API_VERSION"] = IEX_API_VERSION

class stock_obj():
    """
    Data class for stock information returned by IEX finance API
    """
    def __init__(self, ticker, sandbox_mode=False):
        """
        :param str ticker: Stock ticker name (4 letter code)
        :param bool sandbox_mode: Sets API to call from sandbox to preserve message request quota
        """
        self.cloud_box = "sandbox" if sandbox_mode else "cloud"
        self.url_base = f"https://{self.cloud_box}.iexapis.com/stable"
        self.ticker = ticker
        self.set_API_token()
        self.set_api()


    def set_api(self):
        self.api = Stock(self.ticker, token=self.API_TOKEN, output_format="json")

    def set_API_token(self):
        """
        We dont want the actual API key on git for everyone to see so its stored locally and
        not ignored by git. This just loads in either the cloud or sandbox API key for the stock
        """
        with open(f"{self.cloud_box.upper()}_API_KEY", "r") as f:
            self.API_TOKEN = str(f.readline()).strip()
            self.token = f"?token={self.API_TOKEN}"

    def set_price_cur(self):
        today = datetime.date.today()
        today = today.strftime("%Y%m%d")
        url = f"{self.url_base}/stock/{self.ticker}/chart/{today}/{self.token}"
        self.price_cur = requests.get(url).json()[0]

    def set_price_4yr(self):
        today = datetime.date.today()
        today = today.replace(year=today.year-4)
        today = today.strftime("%Y%m%d")
        url = f"{self.url_base}/stock/{self.ticker}/chart/{today}/{self.token}"
        self.price_4yr = requests.get(url).json()[0]

    def get_time_series(self, data="REPORTED_FINANCIALS"):
        test_url = f"{self.url_base}/stock/{self.ticker}/quote/latestPrice{self.token}"
        url = f"{self.url_base}/time-series/{data}/{self.ticker}/{self.token}"
        response = requests.get(url)
        for key, val in response.json()[0].items():
            print(key, val)

    def value_price(self, price_att="price_cur"):
        """
        :param str price_att: Either price_cur or price_historic
        Gives stock value based on price and past price
        """
        scores = [(0, 1), (1, 2), (2, 5), (5, 10), (10, 15),
                  (15, 20), (20, 30), (30, 50), (50, 100), (100,999999999)]
        for i, lims in enumerate(scores):
            price = getattr(self, price_att)["close"]
            if (price >= lims[0]) and (price < lims[1]):
                print(price, lims)
                return i+1
        return 0

def main():
    activate_sandbox_mode()
    stocks = ["AAPL", "TSLA", "MSFT"]
    Tesla = stock_obj(random.choice(stocks), sandbox_mode=True)
    print(Tesla.ticker)
    Tesla.set_price_cur()
    Tesla.set_price_4yr()
    print(Tesla.value_price("price_cur"))
    print(Tesla.value_price("price_4yr"))

if __name__ == "__main__":
    main()


"""
print(price_history[0]) --> 
{
    'close': 627.96,
    'high': 648,
    'low': 611.9,
    'open': 636.52,
    'symbol': 'TSLA',
    'volume': 47152004,
    'id': 'IRCIROS_AHLCIESPT',
    'key': 'SLAT',
    'subkey': '0',
    'date': '2020-12-11',
    'updated': 1665606744432,
    'changeOverTime': -0.027419367716102334,
    'marketChangeOverTime': -0.028016315174162698,
    'uOpen': 620.52,
    'uClose': 639.86,
    'uHigh': 638,
    'uLow': 609.9,
    'uVolume': 48141038,
    'fOpen': 616.61,
    'fClose': 611.86,
    'fHigh': 625,
    'fLow': 617.3,
    'fVolume': 46553367,
    'label': 'Dec 11, 20',
    'change': -17.5287350184907,
    'changePercent': -0.0274}
"""

