import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc3_cfg_cr_if_IH(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['stk_index_corr_sh50', 'close', 'open', 'high', 'low', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '(-0.5,1]'
    handle_preadj = True
    
    def calculate(self, data):
        stk_index_corr = data['stk_index_corr_sh50'].values[-80:]
        stk_close = data['close_preadj'].values[-80:]
        stk_high = data['high_preadj'].values[-80:]
        stk_low = data['low_preadj'].values[-80:]
        stk_open = data['open_preadj'].values[-80:]
        stk_index_corr_rank_mask = section_rank_np(stk_index_corr, pct=True) * 2 - 1
        a = replace_zero(stk_high - stk_low)
        b = stk_close - stk_open
        b[b<0] = np.nan
        factor_init = ts_sum(b / a, 60)
        factor_raw = np.nansum(factor_init * stk_index_corr_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 20)
        return factor_mean[-1]
