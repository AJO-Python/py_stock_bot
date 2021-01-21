# -*-coding: UTF-8-*-
import os
import sys
import random
import requests
import pickle
from StockObj import StockObj
from bs4 import BeautifulSoup

def main(load=False, sandbox=True, N=5):
    if load:
        print("Loading stocks from file...")
        stored_stocks = load_stocks(filename=f"stock_data_{'sandbox' if sandbox else 'cloud'}")
    else:
        setup_environment(sandbox_mode=sandbox)
        print("Scraping company tickers from wikipedia...")
        tickers = scraper("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
        company_values = {}
        stored_stocks = []
        print("Starting API process...")
        for tick in tickers[:int(N)]:
            stock = StockObj(tick, sandbox_mode=sandbox)
            stored_stocks.append(stock)
        print("=======================")
        print("Finished API")
        save_stocks(stored_stocks, filename=f"stock_data_{'sandbox' if sandbox else 'cloud'}")
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

def setup_environment(sandbox_mode=True):
    if sandbox_mode:
        IEX_API_VERSION = "iexcloud-sandbox"
        os.environ["IEX_API_VERSION"] = IEX_API_VERSION
    else:
        pass

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
    # python3 <load|scrape> <cloud|sandbox> <num_companies>
    print(sys.argv)
    if len(sys.argv) == 4:
        num_companies = sys.argv[3]
    else:
        num_companies = 5
    sandbox = sys.argv[2]
    # Safety check. Any argument other than "cloud" will use the sandbox API to save messages
    if sandbox != "cloud":
        sandbox_flag = True
    else:
        sandbox_flag = False

    if sys.argv[1] == "load":
        main(load=True, sandbox=sandbox_flag, N=num_companies)
    elif sys.argv[1] == "scrape":
        main(load=False, sandbox=sandbox_flag, N=num_companies)

