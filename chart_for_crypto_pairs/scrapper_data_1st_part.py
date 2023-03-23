from functions_and_consts import *
# 1
# # Отримання книги ордерів для пари торгів BTCUSDT з глибиною 5


def get_orders_book():
    url = 'https://api.binance.com/api/v3/depth'
    params = {'symbol': 'BTCUSDT', 'limit': 5}
    # розбить на 10 и высчитать средний у каждого
    response = requests.get(url, params=params)

    # Перевірка коду відповіді
    if response.status_code == 200:
        # Парсинг відповіді JSON
        data = response.json()
        bids = data['bids']
        asks = data['asks']

        print('Bids:')
        for bid in bids:
            print(bid)

        print('Asks:')
        for ask in asks:
            print(ask)
    else:
        print(f'Error {response.status_code}: {response.text}')


# 2 Quotation history;
def quote_history(symbol='BTCUSDT'):
    interval = '1h'
    response = get_response(symbol=symbol, interval=interval, limit=24*30)
    data = [[item[0], round(float(item[1]), 2)] for item in response]
    df = pd.DataFrame(data, columns=['date', 'price'])
    df['date'] = pd.to_datetime(df['date'], unit='ms')
    return df


# 3 alt-season index
def get_index_alt_season():
    url = 'https://api.binance.com/api/v3/klines'
    params = {'symbol': 'BTCUSDT', 'interval': '1d', 'limit': 90}
    response = requests.get(url, params=params).json()

    # Calculate the price change for the last 90 days
    btc_prices = [float(x[1]) for x in response]
    btc_price_change = (btc_prices[-1] - btc_prices[0]) / btc_prices[0]

    # Get a list of all trading pairs on Binance
    exchange_info_url = 'https://api.binance.com/api/v3/exchangeInfo'
    exchange_info = requests.get(exchange_info_url).json()
    symbols = [x['symbol'] for x in exchange_info['symbols']]

    # Get data for the last 90 days for each trading pair
    altcoins = {}
    not_alt = ['BTCUSDT']
    for symbol in symbols:
        # Filter only those trading pairs that have USDT
        # as quote currency
        if symbol.endswith('USDT') and symbol not in not_alt:
            params = {'symbol': symbol, 'interval': '1d', 'limit': 90}
            response = requests.get(url, params=params).json()
            altcoin_prices = [float(x[1]) for x in response]
            altcoins[symbol] = {'price_change': (altcoin_prices[-1] - altcoin_prices[0]) / altcoin_prices[0]}
        if len(altcoins) > 50:
            break

    # Calculate the percentage of cryptocurrencies that showed better
    # dynamics than bitcoin
    altcoins_better_than_btc = sum([1 for coin in altcoins.values()
                                    if coin['price_change'] > btc_price_change])
    altcoins_percent = altcoins_better_than_btc / len(altcoins)
    print(altcoins_percent)
    # Определяем, является ли текущий период альтсезоном
    alt_season = altcoins_percent >= 0.75


# 4 index greed and fear
def get_greed_and_fear():
    resp = requests.get('https://api.alternative.me/fng/')
    if resp.status_code == 200:
        return resp.json().get('data')[0].get('value')
    return 'Connection error'


# 5 dollar index
def parse_dollar_index():
    # send a request to a site that provides information about the dollar index
    url = 'https://www.marketwatch.com/investing/index/dxy'
    response = requests.get(url)

    # use bs4 for parse html in page
    soup = BeautifulSoup(response.content, 'html.parser')

    # find page's element, containing info about dollar's index
    index_element = soup.find('bg-quote', {'field': 'Last'})

    # get value dollar's index from element
    dollar_index = index_element.text

    return dollar_index


# 6 index SNP500;
def parse_sp500():
    url = 'https://www.marketwatch.com/investing/index/spx'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    value = soup.find('span', {'class': 'value'})
    return value.text


# 7 gold price
def parse_gold_contrac():
    url = 'https://www.marketwatch.com/investing/future/gc00'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    value = soup.find('h2', {'class': 'intraday__price'}).find('bg-quote')
    return value.text


# 8 silver price
def parse_silver_contrac():
    url = 'https://www.marketwatch.com/investing/future/si00'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    value = soup.find('h2', {'class': 'intraday__price'}).find('span')
    return value.text
