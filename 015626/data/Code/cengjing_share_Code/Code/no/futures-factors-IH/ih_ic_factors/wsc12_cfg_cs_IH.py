import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc12_cfg_cs_IH(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['stk_index_corr_sh50', 'close', 'high', 'low', 'open', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-33:]
        stk_high = data['high_preadj'].values[-33:]
        stk_low = data['low_preadj'].values[-33:]
        stk_open = data['open_preadj'].values[-33:]
        stk_index_corr = data['stk_index_corr_sh50'].iloc[-33:]
        stk_price = (stk_high + stk_low + stk_open + stk_close) / 4
        n = 30
        rpp = ts_sum(stk_price, n)
        high_n = ts_max(stk_high, n)
        low_n = ts_min(stk_low, n)
        temp = replace_zero(high_n - low_n)
        arpp = (rpp - low_n) / temp
        factor_raw = np.nansum(-arpp * stk_index_corr, axis=1)
        factor_mean = ts_mean(factor_raw, 3)
        return factor_mean[-1]
