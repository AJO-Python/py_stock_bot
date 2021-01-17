# -*-coding: UTF-8-*-
import os
import sys
import random
import requests
import pickle
from StockObj import StockObj
from bs4 import BeautifulSoup

def main(load=False):
    if not load:
        activate_sandbox_mode()
        print("Scraping company tickers from wikipedia...")
        tickers = scraper("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
        company_values = {}
        stored_stocks = []
        print("Starting API process...")
        for tick in tickers[:3]:
            stock = StockObj(tick, sandbox_mode=True)
            stored_stocks.append(stock)
        print("=======================")
        print("Finished API")
        save_stocks(stored_stocks)
    else:
        print("Loading stocks from file...")
        stored_stocks = load_stocks()
    
    company_values = get_top_companies(stored_stocks)
    print(sorted(company_values.items()))

def get_top_companies(stocks):
    comp_dict = {}
    for comp in stocks:
        comp_dict[comp.ticker] = comp.value
    return comp_dict

    
def save_stocks(stocks, filename="stock_data"):
    print(f"Saving stocks to {filename}.pickle")
    with open(f"{filename}.pickle", "wb") as output:
        pickle.dump(stocks, output, pickle.HIGHEST_PROTOCOL)
    print("Stocks saved successfully")

def load_stocks(filename="stock_data"):
    print(f"Loading stocks from {filename}.pickle")
    with open(f"{filename}.pickle", "rb") as pickled_data:
        stocks =  pickle.load(pickled_data)
        print("Stocks loaded successfully")
        return stocks

def activate_sandbox_mode():
    # Using the sandbox gives randomised data but gives unlimited requests for testing purposes
    IEX_API_VERSION = "iexcloud-sandbox"
    os.environ["IEX_API_VERSION"] = IEX_API_VERSION

def scraper(url):
    s  = requests.Session()
    # Fetch data from URL
    response = s.get(url, timeout=10)
    # Parse HTMML out for use
    soup = BeautifulSoup(response.text, features="lxml")
    # Get table containing company data
    table = soup.find(id="constituents")
    # Get the div containing the stock ticker
    ticker_divs = table.find_all("a", class_="external text")
    tickers = [i.text for i in ticker_divs if i.text != "reports"]
    # V Uncomment to write stock tickers to a file to check scraper is working correctly
    #print("\n".join(tickers), file=open(f"tickers-{.txt", "w"))
    return tickers


if __name__ == "__main__":
    print(sys.argv)
    if sys.argv[1] == "load":
        main(load=True)
    elif sys.argv[1] == "scrape":
        main(load=False)

