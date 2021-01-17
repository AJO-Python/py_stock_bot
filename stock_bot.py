# -*-coding: UTF-8-*-
import os
import random
from StockObj import StockObj

def main():
    activate_sandbox_mode()
    stocks = ["AAPL", "TSLA", "MSFT"]
    test_stock = StockObj(random.choice(stocks), sandbox_mode=True)
    print("Final stock value: ", test_stock.value)

def activate_sandbox_mode():
    # Using the sandbox gives randomised data but gives unlimited requests for testing purposes
    IEX_API_VERSION = "iexcloud-sandbox"
    os.environ["IEX_API_VERSION"] = IEX_API_VERSION

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

