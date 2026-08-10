import numpy as np
import pandas as pd
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


def ts_midpoint(data, d):
    return (data + ts_delay(data, d)) / 2


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


class wsc_spot_12_srch_if(FutureFactor):
    """
    搜索因子改写
    """
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Index_Id'] = {'000300.SH':['close', 'low']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        spot_close = data['close_000300.SH'].values[-82:]
        spot_low = data['low_000300.SH'].values[-82:]
        
        sc_to_sl = spot_close / spot_low
        factor = ts_midpoint(bbands(sc_to_sl, 9, 2)[2], 72)
        return factor[-1]
