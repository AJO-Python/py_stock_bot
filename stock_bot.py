# -*-coding: UTF-8-*-
import os
import random
import requests
from StockObj import StockObj
from bs4 import BeautifulSoup
def main():
    #activate_sandbox_mode()
    #stocks = ["AAPL", "TSLA", "MSFT"]
    #test_stock = StockObj(random.choice(stocks), sandbox_mode=True)
    tickers = scraper("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    company_values = {}
    for tick in tickers[:10]:
        stock = StockObj(tick, sandbox_mode=True)
        company_values[tick] = stock.value
    print(sorted(company_values.items()))


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
    main()


