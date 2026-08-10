import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero


def atr(price_high, price_low, price_close, time_period=14):
    # ATR(average true range)技术指标，用于衡量市场波动，波动越大则值越大
    true_high = np.maximum(price_high, ts_delay(price_close, 1))
    true_low = np.minimum(price_low, ts_delay(price_close, 1))
    price_tr = true_high - true_low
    # price_tr = np.maximum(np.maximum(abs(price_high - price_low), abs(price_high - ts_delay(price_close, 1))),
    #                       abs(price_low - ts_delay(price_close, 1)))  # 两种算法等价
    price_atr = ts_mean(price_tr, time_period)
    return price_atr


def di(price_high, price_low, price_close, time_period=14):
    # 动量指标
    max_high = ts_delta(price_high, 1)
    max_high[max_high < 0] = 0
    max_low = -ts_delta(price_low, 1)
    max_low[max_low < 0] = 0
    xpdm = ts_delta(price_high, 1)
    xpdm[max_high <= max_low] = 0
    pdm = ts_mean(xpdm, time_period)
    xndm = -ts_delta(price_low, 1)
    xndm[max_low <= max_high] = 0
    ndm = ts_mean(xndm, time_period)
    price_atr = atr(price_high, price_low, price_close, time_period)
    di_plus = pdm / price_atr
    di_minus = ndm / price_atr
    return di_plus, di_minus

    
class wsc_hf_11_srch_if_IM(FutureFactor):

    """
    -div2(di_plus(fh_to_fl, bun, bun, 10), sun)
    """
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'SellUniqueOrderNum']
    data_dict['Index_Id'] = {'000852.SH':['high', 'low']} 
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy_unique_num = data['BuyUniqueOrderNum'].values[-12:]
        sell_unique_num = data['SellUniqueOrderNum'].values[-12:]
        future_high = data['high_000852.SH'].values[-12:]
        future_low = data['low_000852.SH'].values[-12:]
        
        bun = np.nansum(buy_unique_num, axis=1)
        sun = np.nansum(sell_unique_num, axis=1)
        fh_to_fl = (future_high / future_low).reshape(-1,)
        
        factor_init_1 = np.maximum(bun, fh_to_fl)
        factor_init_2 = np.minimum(bun, fh_to_fl)
        
        factor = -di(factor_init_1, factor_init_2, bun, 10)[0] / sun
        return factor[-1]

        