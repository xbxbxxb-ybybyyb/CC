import numpy as np
import bottleneck as bk
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


def section_rank_bk(data, pct=False):
    # numpy的argsort函数在值相同的情况下会出现排序不稳定的情况，所以用bk.rankdata代替，对应df.rank(method='first')
    if not isinstance(data, np.ndarray):
        raise TypeError('Only supports the following type: np.ndarray')
    data_argsort = bk.rankdata(data, axis=1)
    data_argsort[np.isnan(data)] = np.nan  # numpy argsort会让nan也参与排序，但是pandas不会，所以把这些值重新置为nan
    if pct == True:
        data_argsort = data_argsort / (~np.isnan(data)).sum(axis=1, keepdims=True)
    return data_argsort


class wsc13_cfg_vr_if_IM(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'low', 'high', 'open', 'stk_volatility', 'adjfactor']
    normalize_size = 480
    normalize_type = 'ts_rank' 
    
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-47:]
        stk_low = data['low_preadj'].values[-47:]
        stk_open = data['open_preadj'].values[-47:]
        stk_high = data['high_preadj'].values[-47:]
        stk_volatility_hs300 = data['stk_volatility'].values[-47:]
        
        vol_rank = section_rank_bk(stk_volatility_hs300, pct=True) * 2 - 1
        stk_price = (stk_close + stk_low + stk_high + stk_open) / 4
        n = 45
        rpp = ts_sum(stk_price, n)
        high_n = ts_max(stk_high, n)
        low_n = ts_min(stk_low, n)
        arpp = (rpp - low_n) / replace_zero(high_n - low_n)
        factor_raw = np.nansum(arpp * vol_rank, axis=1)
        factor_mean = ts_mean(factor_raw, 2)
        return factor_mean[-1]
    

