## py_stock_bot

### Web scraper
- Gets the S&P 500 company stock tickers to use as input to value the stocks
- Wikipedia should be a stable and up to date source for the tickers

### Stock attributes
- Stock price > $100
    - ~~APi call~~
    - ~~Write value calculation function~~
- Stock price > $100 4yrs ago
    - ~~APi call~~
    - ~~Write value calculation function~~
- Stock price trending upwards from 4yrs ago
    - ~~APi call~~
    - ~~Write value calculation function~~
        - Find % difference between stock price
- Stock with book value > $100
    - ~~APi call~~
    - ~~Write value calculation function~~
        - API returns price-to-book ratio
        - Divide current price by P2B 
- Stock price > 50% of book value
    - ~~APi call~~
    - ~~Write value calculation function~~
        - Compare stock price and book price
- 5 or more analysts rating "buy"
    - API call is setup but getting data requires premium plan
    - ~~Write value calculation function~~
        - Uses "ratingBuy" from API
- 5 or more analysts rating "strong buy"
    - API call is setup but getting data requires premium plan
    - ~~Write value calculation function~~
        - Uses "ratingOverweight" from API
- Dividend yield % between 7.50% and 10.49%
    - ~~API call~~
        - Divide annual dividends paid by price per share
        - Sum all dividend declarations over the past year (APi returns dict for each dividend payment)
    - ~~Write value calculation function~~
        - Check for no dividend as an ege case
- Operating margin > 79.50%
    - ~~API call~~
        - Is included with stock.adv_stats()
    - ~~Value calculation function written~~
- Average daily volume of shares traded > 2,000,000
    - ~~API call~~
        - volume-by-venue call
        - sum by venue to get total volume
    - ~~Value calculation function written~~
- Price to Earning ratio between 0.1x-5.49x
    - Value calculation function written

### API info to look at
- GET /stock/{symbol}/stats/
    - avg10Volume
    - avg30Volume
    - dividendYield
    - peRatio
    - ChangePercent for 1, 2, 5 years

### Example output
    Initialising MSFT...
    In 'sandbox' mode
    Setting API token
    API connected
    Making API calls...
    quote_param: previousVolume: 30382680
    Finished API calls
    Valuing stock...
    Price (price_cur): 220.31 -> 10
    Price (price_4yr): 219.44 -> 10
    Price trend: -0.39646372584761025 -> 6
    Book price: 16.453323375653472 -> 6
    Price to Book: 13.39 -> 1
    Dividends: 0.96 -> 1
    Margins: 0.3315750700073158 -> 0
    Volumes: 32272011 -> 10
    Price to Earnings: 35.45354953288813 -> 5
    Finished valuing stock
    MSFT total value: 49
    MSFT took 6.40 seconds to finish
    Final stock value:  49


### API example
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
