import requests


URL = 'https://api.binance.com/api/v3/klines'


def get_response(symbol, interval, limit):
    params = {'symbol': symbol, 'interval': interval, 'limit': limit}
    response = requests.get(URL, params=params).json()
    # 1 Timestamp in milliseconds (timestamp) is the start time of the candle.
    # 2 The opening price (open) for the specified period.
    # 3 The price of the maximum value (high) for the specified period.
    # 4 The price of the minimum value (low) for the specified period.
    # 5 The closing price (close) for the specified period.
    # 6 Volume (volume) for the specified period.
    # Timestamp in milliseconds (timestamp) is the end time of the candle.
    return response
