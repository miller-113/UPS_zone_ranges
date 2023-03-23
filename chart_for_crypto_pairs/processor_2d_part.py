import math
import requests
import statistics

# from functions_and_consts import *


def get_bid_ask(symbol):
    depth_data = requests.get(f'https://api.binance.com/api/v3/depth?symbol='
                              f'{symbol}&limit=5').json()

    # Get the best bid and best ask from the order book depth data
    best_bid_price = float(depth_data['bids'][0][0])
    best_ask_price = float(depth_data['asks'][0][0])

    # Calculate spread
    spread = (best_ask_price - best_bid_price) / best_ask_price
    return f"Spread for {symbol}: {spread:.4%}"


# # высчитать валуе, получить средний за день, поделить на средний за месяц
# # 2 ⦁	індекс об’єму;
#
# # import requests
# #
# # # Указываем пары для получения данных
# # pair = 'BTCUSDT'
# # url = 'https://api.binance.com/api/v3/klines'
# #
# # # Задаем интервал времени и количество свечей
# # interval = '1h'
# # limit = 24 * 30
# #
# # # Получаем данные
# # params = {'symbol': pair, 'interval': interval, 'limit': limit}
# # response = requests.get(url, params=params).json()
# # # check and del later
# # dates = [datetime.fromtimestamp(int(str(i[0])[:10])) for i in response]
# # #
# # # Получаем объемы торгов и цены закрытия каждой свечи
# # volumes = [float(item[5]) for item in response] # индекс объема
# # closes = [float(item[4]) for item in response] # индекс закрытия свечи
# #
# # # Считаем индекс объема
# # volume_index = sum(volumes)


def get_volume_index(symbol):
    limit = 24 * 30
    url = 'https://api.binance.com/api/v3/klines'
    params = {'symbol': symbol, 'interval': '1h', 'limit': limit}
    response = requests.get(url, params=params).json()

    # Calculate volume index
    # VI = ((Cn - Cn-1) / Cn-1) * V
    # VI - value of the volume index for the current period
    # Cn - closing price on the current period
    # Cn-1 - closing price on the previous period
    # V - trading volume for the current period
    vi = sum(
        [
            ((float(response[i][4])
              - float(response[i - 1][4]))
             / float(response[i - 1][4]))
            * float(response[i][5])
            for i in range(1, len(response))
        ]
    )
    return vi


def get_index_volatility(symbol):
    limit = 24 * 30  # 30 days
    url = 'https://api.binance.com/api/v3/klines'
    params = {'symbol': symbol, 'interval': '1h', 'limit': limit}
    response = requests.get(url, params=params).json()

    # Get a list of closing prices
    close_prices = [float(item[4]) for item in response]

    # Calculate the percentage change in the closing price
    percent_changes = [
        ((close_prices[i] - close_prices[i - 1]) / close_prices[i - 1]) * 100
        for i in range(1, len(close_prices))
    ]

    # Calculate the standard deviation of percentage changes
    std_dev = statistics.stdev(percent_changes)

    # Calculate the monthly level of volatility
    month_volatility = std_dev * math.sqrt(24 * 30)

    # Display the volatility level
    print(f"Volatility level for {symbol} for the last {limit / 24:.0f}"
          f" days: {month_volatility:.2f}%")


# get_index_volatility("BTCUSDT")


def create_index_from_mini_block(mini_block):
    res = []
    for count, item in enumerate(mini_block):
        for count1, inner_i in enumerate(item):
            max_vol = 0
            count_2 = 0
            for count2, min_block in enumerate(inner_i):
                vol = float(min_block[0]) * float(min_block[1])
                if max_vol < vol:
                    count_2 = count2
                    max_vol = vol
            res.append([count, count1, count_2, max_vol])
    return res


def separate_block_for_support_and_resistance(block):
    res = []
    for count, i in enumerate(block):
        cur_val = 0
        cur_count = 0
        for count1, inner in enumerate(i):
            val = float(inner[0]) * float(inner[1])
            if cur_val < val:
                cur_val = val
                cur_count = count1
        res.append([count, cur_count, cur_val])
    return res


# getting 50 asks and bids with the biggest value
def get_asks_bids(symbol):

    depth_data = requests.get(f'https://api.binance.com/api/v3/depth?symbol'
                              f'={symbol}&limit=1000').json()
    asks = depth_data['asks']
    bids = depth_data['bids']

    # define step for separate by groups
    length = len(asks)
    block_num = 5
    step = int(length / block_num)

    block_asks = []
    block_bids = []

    for i in range(block_num):
        block_asks.append(asks[i*step:(i+1) * step])
        block_bids.append(bids[i*step:(i+1) * step])

    step_mini = int(len(block_asks[0]) / 10)

    mini_block_asks = []
    mini_block_bids = []

    for i in range(block_num):
        mini_block_asks.append([block_asks[i][(m_i * step_mini):
                                              (m_i + 1) * step_mini]
                                for m_i in
                                range(int(len(block_asks[i]) / step_mini))])
        mini_block_bids.append([block_bids[i][(m_i * step_mini):
                                              (m_i + 1) * step_mini]
                                for m_i in
                                range(int(len(block_bids[i]) / step_mini))])

    # bids indexes
    mini_block_indexes_bids = create_index_from_mini_block(mini_block_bids)
    # asks indexes
    mini_block_indexes_asks = create_index_from_mini_block(mini_block_asks)

    # return 50 values with the biggest value
    asks_50 = [asks[step*i[0] + step_mini*i[1] + i[2]]
               for i in mini_block_indexes_asks]
    bids_50 = [bids[step*i[0] + step_mini*i[1] + i[2]]
               for i in mini_block_indexes_bids]

    result = {'asks': asks_50, 'bids': bids_50}

    return result


def get_support_and_resistance(symbol):
    data = get_asks_bids(symbol)
    asks = data['asks']
    bids = data['bids']

    # define step for separate by groups
    length = len(asks)
    block_num = 10
    step = int(length / block_num)

    block_asks = []
    block_bids = []
    # separate asks & bids with step 10
    for i in range(step):
        block_asks.append(asks[i*step:(i+1) * step])
        block_bids.append(bids[i*step:(i+1) * step])

    # get indexes for block_bids & block_asks
    support_indexes = separate_block_for_support_and_resistance(block_bids)
    resistance_indexes = separate_block_for_support_and_resistance(block_asks)

    # return list data with (price, vol) with the biggest value
    support_prices = [block_bids[i[0]][i[1]] for i in support_indexes]
    resistance_prices = [block_asks[i[0]][i[1]] for i in resistance_indexes]

    result = {'resistance': resistance_prices, 'support': support_prices}
    # return 5 support levels and 5 resistance
    return result

