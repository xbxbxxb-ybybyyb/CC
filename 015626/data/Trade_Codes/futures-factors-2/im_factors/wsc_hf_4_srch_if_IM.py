import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero


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


class wsc_hf_4_srch_if_IM(FutureFactor):

    """
    搜索因子，factor_raw用主买成交订单数 / 主买独立成交订单数表征单子的金额大小
    再对factor_raw作数学变换后求布林带下轨
    """
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeNum', 'BuyUniqueOrderNum']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy_trade_num = data['BuyTradeNum'].values[-20:]
        buy_unique_order_num = data['BuyUniqueOrderNum'].values[-20:]
        
        factor_init_1 = np.nansum(buy_trade_num, axis=1)
        factor_init_2 = np.nansum(buy_unique_order_num, axis=1)

        factor_raw = factor_init_1 / factor_init_2        
        factor = bbands(square(log(factor_raw)), 20, 2)[2]
        return factor[-1]