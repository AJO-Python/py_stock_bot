# -*-coding: UTF-8-*-
import numpy as np
import json
import requests
import datetime
import time
from iexfinance.stocks import Stock

class StockObj():
    """
    Data class for stock information returned by IEX finance API
    """

    def __init__(self, ticker, sandbox_mode=True, price_key="close"):
        """
        :param str ticker: Stock ticker name (4 letter code)
        :param bool sandbox_mode: Sets API to call from sandbox to preserve message request quota
        """
        start = time.time()
        print("==============================")
        print(f"Initialising {ticker}...")
        self.price_key = price_key
        self.cloud_box = "sandbox" if sandbox_mode else "cloud"
        self.url_base = f"https://{self.cloud_box}.iexapis.com/stable"
        print(f"In '{self.cloud_box}' mode")

        self.ticker = ticker
        print("Setting API token")
        self.set_API_token()
        self.set_api()
        print("API connected")
        print("Making API calls...")
        self.make_api_calls()
        print("Finished API calls")
        print("Valuing stock...")
        self.set_stock_value()
        print("Finished valuing stock")
        print(f"{self.ticker} total value: {self.value}")
        end = time.time()
        self.init_time = end-start
        print(f"{self.ticker} took {self.init_time:.2f} seconds to finish")

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

    def set_stock_value(self):
        self.values = [
            self.value_price("price_cur"),
            self.value_price("price_4yr"),
            self.value_price_trend(),
            self.value_book(),
            self.value_P2B(),
            self.value_analysts(),
            self.value_strong_analysts(),
            self.value_dividends(),
            self.value_margins(),
            self.value_volumes(),
            self.value_P2E()
        ]
        self.value = sum(self.values)

    #######################################################################################
    # API CALLS
    def make_api_calls(self):
        self.set_stats()
        self.set_adv_stats()
        self.set_price_cur()
        self.set_price_4yr()
        self.set_quote_param("previousVolume")
        # self.set_analyst()  # Can uncomment this when we have a paid account
        self.set_dividends()
        self.set_margins()
        self.set_volume()
        self.set_P2E()

    def set_stats(self):
        url = f"{self.url_base}/stock/{self.ticker}/stats/{self.token}"
        self.stats = requests.get(url).json()

    def set_adv_stats(self):
        url = f"{self.url_base}/stock/{self.ticker}/advanced-stats/{self.token}"
        self.adv_stats = requests.get(url).json()

    def set_price_cur(self):
        today = datetime.date.today()
        today = today.strftime("%Y%m%d")
        url = f"{self.url_base}/stock/{self.ticker}/chart/{today}/{self.token}"
        self.price_cur = requests.get(url).json()[0]

    def set_price_4yr(self):
        today = datetime.date.today()
        today = today.replace(year=today.year - 4)
        today = today.strftime("%Y%m%d")
        url = f"{self.url_base}/stock/{self.ticker}/chart/{today}/{self.token}"
        self.price_4yr = requests.get(url).json()[0]

    def set_quote_param(self, param):
        """
        Uses quote API
        Can get and set any parameter that exists as a json key in the quotes API response
        N.B this and set volume give similar but different answers. Maybe difference between live and market close times?
        """
        url = f"{self.url_base}/stock/{self.ticker}/quote/{param}/{self.token}"
        response = requests.get(url).json()
        setattr(self, param, response)

        print(f"quote_param: {param}: {getattr(self, param)}")

    def set_analyst(self):
        try:
            url = f"{self.url_base}/stock/{self.ticker}/recommendation-trends/{self.token}"
        except:
            raise NotImplementedError("INSIDE 'set_analyst()' \nThis function requires a paid account for the API call")
        self.analysts = requests.get(url).json()

    def set_dividends(self, time_period="1y"):
        url = f"{self.url_base}/stock/{self.ticker}/dividends/{time_period}/{self.token}"
        response = requests.get(url).json()
        total_dividend = 0
        for declaration in response:
            total_dividend += float(declaration["amount"])
        self.total_dividend = total_dividend
        self.dividend_yield = self.total_dividend / self.price_cur[self.price_key]

    def set_margins(self):
        self.margin = self.adv_stats["profitMargin"]

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

    def set_P2E(self):
        self.peRatio = self.stats["peRatio"]

    #######################################################################################
    # VALUATION METHODS
    def value_price(self, price_att="price_cur"):
        """
        :param str price_att: Either price_cur or price_historic
        Gives stock value based on either price or past price (max value @ $100)
        """
        scores = {
            (0, 1): 1,
            (1, 2): 2,
            (2, 5): 3,
            (5, 10): 4,
            (10, 15): 5,
            (15, 20): 6,
            (20, 30): 7,
            (30, 50): 8,
            (50, 100): 9,
            (100, float("inf")): 10,
        }
        for lims in scores.keys():
            try:
                price = getattr(self, price_att)[self.price_key]
                if (price >= lims[0]) and (price < lims[1]):
                    print(f"Price ({price_att}): {price:.2f} -> {scores[lims]}")
                    return scores[lims]
            except (AttributeError, JSONDecodeError):
                print("value_price failed.\nSetting value to 0 and moving on...")
        return 0

    def value_price_trend(self):
        """
        Rates highly for stock that has improved over time
        """
        try:
            trend = 100 - ((self.price_cur[self.price_key] * 100) / self.price_4yr[self.price_key])
        except (AttributeError, JSONDecodeError):
            print("value_price_trend failed.\nSetting value to 0 and moving on...")
            return 0
        # print(trend)
        # scores = dict(percentage_range : att_value)
        scores = {
            (float("-inf"), -50.5): 1,
            (-50.5, -11.5): 2,
            (-11.5, -0.5): 5,
            (-0.5, 1, 5): 6,
            (1.5, 10.5): 7,
            (10.5, 99.5): 9,
            (99.5, float("inf")): 10,
        }
        for lims in scores.keys():
            if (trend >= lims[0]) and (trend < lims[1]):
                print(f"Price trend: {trend} -> {scores[lims]}")
                return scores[lims]
        return 0

    def value_book(self):
        """
        Price of stock relative to its book value
        Max value @ $100
        Price/Book Value = P2B ratio
        so Price/P2B = Book Value
        """
        try:
            P2B = self.adv_stats["priceToBook"]
            book_value = self.price_cur[self.price_key] / P2B
        except (AttributeError, JSONDecodeError):
            print("value_book failed.\nSetting value to 0 and moving on...")
            return 0
        scores = {
            (0, 1): 1,
            (1, 2): 2,
            (2, 5): 3,
            (5, 10): 4,
            (10, 15): 5,
            (15, 20): 6,
            (20, 30): 7,
            (30, 50): 8,
            (50, 100): 9,
            (100, float("inf")): 10,
        }
        # print("Book Value: ", self.price_cur[self.price_key]
        # print("p2v: ", P2B)
        # print("Book Value: ", book_value)
        for lims in scores.keys():
            if (book_value >= lims[0]) and (book_value < lims[1]):
                print(f"Book price: {book_value} -> {scores[lims]}")
                return scores[lims]
        return 0

    def value_P2B(self):
        """
        price_cur > (book_value/2)
        """
        try:
            P2B = self.adv_stats["priceToBook"]
        except (AttributeError, JSONDecodeError):
            print("value_P2B failed.\nSetting value to 0 and moving on...")
            return 0
        scores = {
            (float("-inf"), -49.5): 10,
            (-49.5, -10.5): 8,
            (-10.5, -0.5): 6,
            (-0.5, 1, 5): 4,
            (1.5, 9.5): 2,
            (9.5, 99.5): 1,
            (99.5, float("inf")): 0,
        }
        for lims in scores.keys():
            if (P2B >= lims[0]) and (P2B < lims[1]):
                print(f"Price to Book: {P2B} -> {scores[lims]}")
                return scores[lims]
        return 0

    def value_analysts(self):
        """
        5 or more buys
        /recommendation_trends/ratingBuy
        """
        try:
            analysts_buy = self.analysts["ratingBuy"]
        except (AttributeError, JSONDecodeError):
            print("value_analysts failed.\nSetting value to 0 and moving on...")
            return 0
        scores = {
            (0): 0,
            (1): 2,
            (2, 3): 3,
            (4, 5): 4,
            (5, float("inf")): 5,
        }
        for val in scores.keys():
            if analysts_buy in val:
                print(f"Analysts buy: {analysts_buy} -> {scores[val]}")
                return scores[val]
        return 0

    def value_strong_analysts(self):
        """
        5 or more strong buys
        /recommendation_trends/ratingOverweight
        """
        try:
            analysts_buy = self.analysts["ratingOverweight"]
        except (AttributeError, JSONDecodeError):
            print("value_strong_analysts failed.\nSetting value to 0 and moving on...")
            return 0
        scores = {
            (0): 0,
            (1): 3,
            (2, 3, 4): 4,
            (5, float("inf")): 5,
        }
        for val in scores.keys():
            if analysts_buy in val:
                print(f"Analysts strong buy: {analysts_buy} -> {scores[val]}")
                return scores[val]
        return 0

    def value_dividends(self):
        """
        7.5% < yield < 10.5
        """
        try:
            dividend_percent = self.dividend_yield * 100
        except (AttributeError, JSONDecodeError):
            print("value_dividends failed.\nSetting value to 0 and moving on...")
            return 0
        scores = {
            (0, 1.50): 1,
            (1.50, 2.50): 4,
            (2.50, 4.50): 6,
            (4.50, 7.50): 8,
            (7.50, 10.50): 10,
            (10, float("inf")): 2,
        }
        for lims in scores.keys():
            if not dividend_percent:
                print("No dividend")
                return 0
            elif (dividend_percent >= lims[0]) and (dividend_percent < lims[1]):
                print(f"Dividends: {dividend_percent:.2f} -> {scores[lims]}")
                return scores[lims]
        return 0

    def value_margins(self):
        """
        Expenses less revenue. Ideally > 80%
        """
        scores = {
            (float("-inf"), 1.50): 0,
            (1.50, 4.50): 1,
            (4.50, 9.50): 2,
            (9.50, 19.50): 3,
            (19.50, 29.50): 4,
            (29.50, 49.50): 6,
            (49.50, 69.50): 8,
            (69.50, 79.50): 9,
            (79.50, float("inf")): 10,
        }
        try:
            for lims in scores.keys():
                if (self.margin >= lims[0]) and (self.margin < lims[1]):
                    print(f"Margins: {self.margin} -> {scores[lims]}")
                    return scores[lims]
        except (AttributeError, JSONDecodeError):
            print("value_margins failed.\nSetting value to 0 and moving on...")
            return 0
        return 0

    def value_volumes(self):
        """
        Ideally more than 2mil traded per day
        """
        scores = {
            (float("-inf"), 10000): 0,
            (10000, 30000): 1,
            (30000, 50000): 2,
            (50000, 100000): 3,
            (100000, 250000): 4,
            (250000, 500000): 5,
            (500000, 750000): 6,
            (750000, 1000000): 8,
            (1000000, 2000000): 9,
            (2000000, float("inf")): 10,
        }
        try:
            for lims in scores.keys():
                if (self.volume >= lims[0]) and (self.volume < lims[1]):
                    print(f"Volumes: {self.volume} -> {scores[lims]}")
                    return scores[lims]
        except (AttributeError, JSONDecodeError):
            print("value_volumes failed.\nSetting value to 0 and moving on...")
            return 0
        return 0

    def value_P2E(self):
        """
        price-to-earnings
        """
        scores = {
            (float("-inf"), 0): 0,
            (0, 5.5): 10,
            (5.5, 15.5): 9,
            (15.5, 20.5): 8,
            (20.5, 25.5): 7,
            (25.5, 30.5): 6,
            (30.5, 35.5): 5,
            (35.5, 40.5): 4,
            (40.5, 100): 2,
            (100, float("inf")): 1
        }
        try:
            for lims in scores.keys():
                if (self.peRatio >= lims[0]) and (self.peRatio < lims[1]):
                    print(f"Price to Earnings: {self.peRatio} -> {scores[lims]}")
                    return scores[lims]
        except (AttributeError, JSONDecodeError):
            print("value_P2E failed.\nSetting value to 0 and moving on...")
            return 0
        return 0

    def get_time_series(self, data="REPORTED_FINANCIALS"):
        test_url = f"{self.url_base}/stock/{self.ticker}/quote/latestPrice{self.token}"
        url = f"{self.url_base}/time-series/{data}/{self.ticker}/{self.token}"
        response = requests.get(url)
        for key, val in response.json()[0].items():
            print(key, val)
