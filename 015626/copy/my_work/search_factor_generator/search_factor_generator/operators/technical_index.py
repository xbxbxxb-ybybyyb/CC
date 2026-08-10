import numpy as np
from .opeartors_wsc import *

__all__ = ['bbands', 'dema', 'kama', 'mavp', 'midpoint', 'midprice', 'trima', 'wma']


def bbands(price, time_period=5, a=2):
    """
    Bollinger Bands：过去一段时间的均价加上/减去过去一段时间价格的标准差
    :param price: array_like
        原始价格序列
    :param time_period: int
        回看长度
    :param a: int
        加减标准差的倍数
    :return: price_ma, price_up_track. price_down_track: array_like
        价格均线，价格上轨，价格下轨
    """
    price_ma = ts_mean(price, time_period)
    price_std = ts_std(price, time_period)
    price_up_track = price_ma + a * price_std
    price_down_track = price_ma - a * price_std
    return price_ma, price_up_track, price_down_track


def dema(price, time_period=30):
    """
    double exponential moving average: 双重指数移动平均
    :param price: array_like
        原始价格序列
    :param time_period: int
        回看长度
    :return: array_like
        dema of price
    """
    price_ema = ts_ema_span(price, time_period)
    price_dema = 2 * price_ema - ts_ema_span(price_ema, time_period)
    return price_dema


def kama(price, time_period=10, n1=2, n2=30):
    """
    Kaufman's Adaptative Moving Average: 考夫曼自适应移动平均
    When market volatility is low, Kaufman’s Adaptive Moving Average remains near the current market price, but when
    volatility increases, it will lag behind. What the KAMA indicator aims to do is filter out “market noise” –
    insignificant, temporary surges in price action. One of the primary weaknesses of traditional moving averages is
    that when used for trading signals, they tend to generate many false signals. The KAMA indicator seeks to lessen
    this tendency – generate fewer false signals – by not responding to short-term, insignificant price movements.
    :param price: array_like
        原始价格序列
    :param time_period: int
        回看长度
    :param n1: int
        快速移动平均周期
    :param n2: int
        慢速移动平均周期
    :return: array_like
        kama of price
    """
    change = abs(ts_delta(price, time_period))
    volatility = ts_sum(abs(ts_delta(price, 1)))
    er = change / volatility
    fast_sc = 2 / (n1 + 1)
    slow_sc = 2 / (n2 + 1)
    smooth_constant = er * (fast_sc - slow_sc) + slow_sc
    cof = smooth_constant ** 2
    price_kama = price.ema(alpha=cof, adjust=False).mean()
    return price_kama


def mavp(price, va_time_period, min_period, max_period):
    """
    MAVP - Moving average with variable period.
    It gets an input price array, and a period array that are the same length.
    The output price array is the moving average at the point using the specified period at the point.
    So, if you have an array of [1, 5, 3, 8] and you specify period [2,3,3,2] then the output will be:
    [MA(2)[0], MA(3)[1], MA(3)[2], MA(2)[3]]
    With the exception that it puts maxperiod number of nan's at the front, for some reason so you'd need to call it like:

    example:
    price = np.array([1,5,7,8], dtype=float)
    va_time_period =np.array([2,3,3,2], dtype=float)
    mavp(price, period, maxperiod=3)
    array([nan, nan, 4.33333333, 7.5])

    ts_mean(price, 2)
    array([ nan, 3., 6., 7.5])

    ts_mean(price, 3)
    array([nan, nan, 4.33333333, 6.66666667])

    :param price: array_like
        原始价格序列
    :param va_time_period: array_like
        可变回看序列
    :param min_period: int
        最短回看长度
    :param max_period: int
        最长回看长度
    :return: array_like
        price of mavp
    """
    price_mavp = np.empty_like(price)
    va_time_period[va_time_period < min_period] = min_period
    va_time_period[va_time_period > max_period] = max_period
    va_time_period_unique = np.unique(va_time_period)
    average_array = np.empty(shape=(len(va_time_period_unique), len(price)))
    for i, i_num in enumerate(va_time_period_unique):
        average_array[i] = ts_mean(price, i_num)
    for j, j_num in va_time_period:
        index_va_time_period = np.argwhere(va_time_period_unique == j_num)
        price_mavp[j] = average_array[index_va_time_period, j]
    return price_mavp


def midpoint(price, time_period):
    """
    (highest value + lowest value)/2
    :param price: array_like
        原始价格序列
    :param time_period: int
        回看时间长度
    :return: array_like
        midpoint of price
    """
    highest_price = ts_max(price, time_period)
    lowest_price = ts_min(price, time_period)
    price_midpoint = (highest_price + lowest_price) / 2
    return price_midpoint


def midprice(price_high, price_low, time_period):
    """
    (highest high + lowest low) / 2
    :param price_high: array_like
        原始高价序列
    :param price_low: array_like
        原始低价序列
    :param time_period: int
        回看时间长度
    :return: array_like
        midprice of price
    """
    highest_price = ts_max(price_high, time_period)
    lowest_price = ts_min(price_low, time_period)
    price_midprice = (highest_price + lowest_price) / 2
    return price_midprice


def trima(price, time_period):
    if time_period % 2 == 0:
        price_trima = ts_mean(ts_mean(price, int(time_period / 2 + 1)), int(time_period / 2))
    else:
        price_trima = ts_mean(ts_mean(price, int((time_period + 1) / 2)), int((time_period + 1) / 2))
    return price_trima


def wma(price, time_period):
    return ts_decay_linear(price, time_period)
