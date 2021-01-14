# -*-coding: UTF-8-*-
import numpy as np
import json
import requests
import datetime
from iexfinance.stocks import Stock


class StockObj():
    """
    Data class for stock information returned by IEX finance API
    """
    def __init__(self, ticker, sandbox_mode=False, price_key="close"):
        """
        :param str ticker: Stock ticker name (4 letter code)
        :param bool sandbox_mode: Sets API to call from sandbox to preserve message request quota
        """
        self.price_key = price_key
        self.cloud_box = "sandbox" if sandbox_mode else "cloud"
        self.url_base = f"https://{self.cloud_box}.iexapis.com/stable"
        self.ticker = ticker
        self.set_API_token()
        self.set_api()
        self.make_api_calls()

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

    def stock_value(self):
        self.values = [
            self.value_price("price_cur"),
            self.value_price("price_4yr"),
            self.value_price_trend(),
            self.value_book(),
            self.value_V2P(),
            self.value_analysts(),
            self.value_strong_analysts(),
            self.value_dividends(),
            self.value_margins(),
            self.value_volumes(),
            self.value_P2E()
            ]
        self.value = sum(self.values)
        return self.value

#######################################################################################
# API CALLS
    def make_api_calls(self):
        self.set_price_cur()
        self.set_price_4yr()
        self.set_adv_stats()
        self.set_volume()
        self.set_quote_param("previousVolume")
        self.set_analyst() #Can uncomment this when we have a paid account
        self.set_dividends()

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

    def set_adv_stats(self):
        url = f"{self.url_base}/stock/{self.ticker}/advanced-stats/{self.token}"
        self.adv_stats = requests.get(url).json()

    def set_volume(self):
        """
        Uses volume-by-venue API call
        Response object is a list of dicts by market --> sums total volume over all markets
        """
        url = f"{self.url_base}/stock/{self.ticker}/volume-by-venue/{self.token}"
        volume = 0
        volume_raw = requests.get(url).json()
        for volume_dict in volume_raw:
            volume += volume_dict["volume"]
        self.volume = volume
        print(self.volume)

    def set_quote_param(self, param):
        """
        Uses quote API
        Can get and set any parameter that exists as a json key in the quotes API response
        N.B this and set volume give similar but different answers. Maybe difference between live and market close times?
        """
        print("quote_param: ")
        url = f"{self.url_base}/stock/{self.ticker}/quote/{param}/{self.token}"
        response = requests.get(url).json()
        setattr(self, param, response)
        print(getattr(self, param))

    def set_analyst(self):
        #raise NotImplementedError("INSIDE 'set_analyst()' \nThis function requires a paid account for the API call")
        url = f"{self.url_base}/stock/{self.ticker}/recommendation-trends/{self.token}"
        response = requests.get(url)
        print(f"set_analyst() returns: {response}")

    def set_dividends(self):
        url = f"{self.url_base}/stock/{self.ticker}/dividends/1y/{self.token}"
        response = requests.get(url).json()
        print(response)






#######################################################################################
# VALUATION METHODS
    def value_price(self, price_att="price_cur"):
        """
        :param str price_att: Either price_cur or price_historic
        Gives stock value based on either price or past price (max value @ $100)
        """
        scores = {
                (0, 1)              :1,
                (1, 2)              :2,
                (2, 5)              :3,
                (5, 10)             :4,
                (10, 15)            :5,
                (15, 20)            :6,
                (20, 30)            :7,
                (30, 50)            :8,
                (50, 100)           :9,
                (100, float("inf")) :10,
                }
        for i, lims in enumerate(scores):
            price = getattr(self, price_att)[self.price_key]
            if (price >= lims[0]) and (price < lims[1]):
                return i+1
        return 0

    def value_price_trend(self):
        """
        Rates highly for stock that has improved over time
        """
        trend = 100 - ((self.price_cur[self.price_key]*100) / self.price_4yr[self.price_key])
        #print(trend)
        # scores = dict(percentage_range : att_value)
        scores = {
                (float("-inf"), -50.5)  : 1,
                (-50.5, -11.5)          : 2,
                (-11.5, -0.5)           : 5,
                (-0.5, 1,5)             : 6,
                (1.5, 10.5)             : 7,
                (10.5, 99.5)            : 9,
                (99.5, float("inf"))    : 10,
                } 
        for lims in scores.keys():
            if (trend >= lims[0]) and (trend < lims[1]):
                return scores[lims]
        return 0

    def value_book(self):
        """
        Price of stock relative to its book value
        Max value @ $100
        Price/Value = P2V ratio
        so Price/P2V = Value
        """
        P2V = self.adv_stats["priceToBook"]
        book_value = self.price_cur[self.price_key]/P2V
        scores = {
                (0, 1)              :1,
                (1, 2)              :2,
                (2, 5)              :3,
                (5, 10)             :4,
                (10, 15)            :5,
                (15, 20)            :6,
                (20, 30)            :7,
                (30, 50)            :8,
                (50, 100)           :9,
                (100, float("inf")) :10,
                }
        #print("Value: ", self.price_cur[self.price_key]
        #print("p2v: ", P2V)
        #print("Book value: ", book_value)
        for lims in scores.keys():
            if (book_value >= lims[0]) and (book_value < lims[1]):
                return scores[lims]
        return 0


    def value_V2P(self):
        """
        price_cur > (book_value/2)
        """
        P2V = self.adv_stats["priceToBook"]
        scores = {
                (float("-inf"), -49.5)  : 10,
                (-49.5, -10.5)          : 8,
                (-10.5, -0.5)           : 6,
                (-0.5, 1,5)             : 4,
                (1.5, 9.5)             : 2,
                (9.5, 99.5)            : 1,
                (99.5, float("inf"))    : 0,
                } 
        for lims in scores.keys():
            if (P2V >= lims[0]) and ( P2V < lims[1]):
                return scores[lims]
        return 0

    def value_analysts(self):
        """
        5 or more buys
        """
        return 0

    def value_strong_analysts(self):
        """
        5 or more strong buys
        """
        return 0

    def value_dividends(self):
        """
        7.5% < yield < 10.5
        """
        return 0

    def value_margins(self):
        """
        Expenses less revenue. Ideally > 80%
        """
        return 0

    def value_volumes(self):
        """
        Ideally more than 2mil traded per day
        """
        return 0

    def value_P2E(self):
        """
        price-to-earnings
        """
        return 0

    def get_time_series(self, data="REPORTED_FINANCIALS"):
        test_url = f"{self.url_base}/stock/{self.ticker}/quote/latestPrice{self.token}"
        url = f"{self.url_base}/time-series/{data}/{self.ticker}/{self.token}"
        response = requests.get(url)
        for key, val in response.json()[0].items():
            print(key, val)




