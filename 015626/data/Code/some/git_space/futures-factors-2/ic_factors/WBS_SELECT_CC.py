import numpy as np
import numpy.ma as ma
from operators_cc import *
from future_factor import FutureFactor
from operators_wsc_1_0 import *
import numpy.ma as ma
import bottleneck as bk

def ts_truncated_ema_1(data, d, alpha):
    # truncated ema
    if (alpha >= 1) or (alpha <= 0):
        raise ValueError('`alpha` must be in (0, 1)')
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    return ts_decay_linear(data=data, d=d, weight=weight)


def ts_truncated_ema_span_1(data, d, span):
    # truncated ema
    return ts_truncated_ema_1(data=data, d=d, alpha=2 / (span + 1))


class WBS_SELECT_CC(FutureFactor):
    
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['WeightSellOrderQtySumMean', 'WeightBuyOrderQtySumMean','BuyUniqueOrderNum','BuyTradeNum', 'SellUniqueOrderNum', 'SellTradeNum']
    normalize_size = 240
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        factor_raw = (data['BuyUniqueOrderNum'].values[-20:] / r(data['BuyTradeNum']).values[-20:]) - (data['SellUniqueOrderNum'].values[-20:] / r(data['SellTradeNum'].values[-20:]))
        df_s = (data['WeightBuyOrderQtySumMean'].values[-20:] / r(data['WeightSellOrderQtySumMean'].values[-20:]))
        
        amount_mask = np.nanquantile(df_s, 0.9, axis=1)
        amount_mask = np.expand_dims(amount_mask, axis=-1)
        
        factor_raw_after_mask = ma.array(factor_raw, mask=(df_s<=amount_mask))
        factor_raw_after_mask = np.nanmean(factor_raw_after_mask, axis=1)
        factor_mean = ts_truncated_ema_span_1(factor_raw_after_mask, 19, 2)[-1]
        return -factor_mean
