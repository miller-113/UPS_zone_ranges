from scrapper_data_1st_part import quote_history
import pandas as pd
import matplotlib.pyplot as plt
from processor_2d_part import get_support_and_resistance
import seaborn as sns
import requests


def chart_quotation_history(symbol):
    data = quote_history(symbol)
    # dates
    x = [i for i in data['date']]
    y = [i for i in data['price']]
    plt.plot(x, y)

    # graph settings
    plt.title('History of quotations')
    plt.xlabel('Date')
    plt.ylabel('Price')

    plt.xticks(rotation=35)
    plt.show()


def chart_with_support_resistance_lvl(symbol):

    data = quote_history(symbol=symbol)
    data_supp_resistance = get_support_and_resistance(symbol)
    support_levels_data = data_supp_resistance.get('support')
    resistance_levels_data = data_supp_resistance.get('resistance')
    support_levels = [float(i[0]) for i in support_levels_data]
    resistance_levels = [float(i[0]) for i in resistance_levels_data]

    # draw support line
    [plt.axhline(y=level, color='green', linewidth=0.6)
     for level in support_levels]
    # draw resistance line
    [plt.axhline(y=level, color='red', linewidth=0.6)
     for level in resistance_levels]

    # data for fulfill chart
    x = [i for i in data['date']]
    y = [i for i in data['price']]
    # create graph
    plt.plot(x, y)

    # graph settings
    plt.title(f'History of quotations {symbol}')
    plt.xlabel('Date')
    plt.ylabel('Price')

    plt.xticks(rotation=35)
    plt.subplots_adjust(bottom=.2)
    plt.show()


def cup_depth_chart(symbol=None):
    depth_data = requests.get(f'https://api.binance.com/api/v3/depth?symbol'
                              f'={symbol}&limit=1000').json()

    df_list = []
    for side in ["bids", "asks"]:
        df = pd.DataFrame(depth_data[side],
                          columns=["price", "quantity"],
                          dtype=float)
        df["side"] = side
        df_list.append(df)

    df = pd.concat(df_list).reset_index(drop=True)


    fig, ax = plt.subplots()
    ax.set_title(f"{symbol} Order Book - Depth Chart")
    sns.ecdfplot(x="price", weights="quantity", stat="count",
                 complementary=True, data=df.query("side == 'bids'"),
                 color="blue", ax=ax)
    sns.ecdfplot(x="price", weights="quantity", stat="count",
                 data=df.query("side == 'asks'"), color="orange",
                 ax=ax)

    sns.scatterplot(x="price", y="quantity", hue="side",
                    data=df, ax=ax, palette=["blue", "orange"])
    ax.set_xlabel("Price")
    ax.set_ylabel("Quantity")
    plt.show()


