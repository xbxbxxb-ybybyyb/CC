import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc14_cfg_cr_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['stk_index_corr_hs300', 'close', 'adjfactor']
    normalize_size = 240*8
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_index_corr = data['stk_index_corr_hs300'].values[-117:]
        stk_close = data['close_preadj'].values[-117:]
        stk_index_corr_rank_mask = section_rank_np(stk_index_corr, pct=True) * 2 - 1
        n = 10
        temp = ts_sum(abs(ts_delta(stk_close, 1)), n)
        vi = abs(ts_delta(stk_close, n)) / replace_zero(temp)
        vidya = vi * stk_close + (1-vi) * ts_delay(stk_close, 1)
        factor_init = rolling_norm(vidya, 90)
        factor_raw = np.nansum(factor_init * stk_index_corr_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        return factor_mean[-1]
