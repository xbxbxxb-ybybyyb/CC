from operators_wsc_1_0 import *
import numpy.ma as ma
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *

def ts_truncated_ema_1(data, d, alpha):
    # truncated ema
    if (alpha >= 1) or (alpha <= 0):
        raise ValueError('`alpha` must be in (0, 1)')
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    return ts_decay_linear(data=data, d=d, weight=weight)


def ts_truncated_ema_span_1(data, d, span):
    # truncated ema
    return ts_truncated_ema_1(data=data, d=d, alpha=2 / (span + 1))


class srch_11(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [ 'BuyUniqueOrderNum', 'BuyTradeNum', 'buy_bigorder_money', 'SellUniqueOrderNum','weight']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-66:]
        BuyTradeNum = data['BuyTradeNum'].values[-66:]
        weight = data['weight'].values[-66:]
        bun_to_bn_w = np.nansum(BuyUniqueOrderNum / replace_zero(BuyTradeNum) * weight, axis = 1) 

        buy_bigorder_money = data['buy_bigorder_money'].values[-236:]
        bba_2 = np.nansum(buy_bigorder_money, axis = 1)
        
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-31:]
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-31:]
        bun_r = np.nansum(BuyUniqueOrderNum, axis = 1) / np.nansum(BuyUniqueOrderNum + SellUniqueOrderNum, axis = 1)
        
        factor =  -add2(aroon(bun_to_bn_w, auto_corr(bba_2, 85, 85)[-66:], 65)[-1], ts_maxmin_distance(bun_r, 30)[-1])
        
        return factor

