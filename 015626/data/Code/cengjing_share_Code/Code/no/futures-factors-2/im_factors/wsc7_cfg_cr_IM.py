import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc7_cfg_cr_IM(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['stk_index_corr_zz1000', 'close', 'high', 'low', 'adjfactor']
    normalize_size = 1800
    normalize_type = 'ts_rank'
#    num_range = '(-0.8,1]'
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-110:]
        stk_high = data['high_preadj'].values[-110:]
        stk_low = data['low_preadj'].values[-110:]
        stk_index_corr_zz500 = data['stk_index_corr_zz1000'].values[-110:]
        stk_index_corr_rank_mask = section_rank_np(stk_index_corr_zz500, pct=True) * 2 - 1
        n = 20
        m = 60
        low_n = ts_min(stk_low, n)
        high_n = ts_max(stk_high, n)
        a = replace_zero(high_n - low_n)
        stochastics = (stk_close- low_n) / a
        stochastics_low = ts_min(stochastics, m)
        stochastics_high = ts_max(stochastics, m)
        c = replace_zero(stochastics_high - stochastics_low)
        stochastics_double = (stochastics - stochastics_low) / c
        factor_raw = np.nansum(stochastics_double * stk_index_corr_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 30)
        return factor_mean[-1]
