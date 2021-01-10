# -*-coding: UTF-8-*-
import tkinter as tk
import pandas as pd
import numpy as np
import os
from iexfinance.stocks import Stock

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

# We dont want the actual API key on git for everyone to see so its stored locally and
# not clided with git. This just loads it in
with open("API_KEY", "r") as f:
    API_TOKEN = str(f.readline()).strip()

# Using the sandbox gives randomised data but gives unlimited requests for testing purposes
IEX_API_VERSION = "iexcloud-sandbox"
os.environ["IEX_API_VERSION"] = IEX_API_VERSION

Tesla = Stock("TSLA", token=API_TOKEN, output_format="json")

Tesla_history = Tesla.get_historical_prices()
# Numpy lets us deal with arrays easier
# Some of the data may come in as Pandas dataframe so can change if needed
price_history = np.array(Tesla_history)
print(price_history)

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

