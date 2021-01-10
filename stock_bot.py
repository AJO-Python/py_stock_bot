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
with open("API_KEY", "r") as f:
    API_TOKEN = str(f.readline()).strip()
IEX_API_VERSION = "iexcloud-sandbox"
os.environ["IEX_API_VERSION"] = IEX_API_VERSION
Tesla = Stock("TSLA", token=API_TOKEN, output_format="pandas")

Tesla_history = Tesla.get_historical_prices()
price_history = np.array(Tesla_history)
print(Tesla_history)
print(price_history)
print(np.shape(price_history))
