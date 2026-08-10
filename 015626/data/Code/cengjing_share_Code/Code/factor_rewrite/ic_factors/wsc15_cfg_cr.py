import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc15_cfg_cr(FutureFactor):
    data_type = 'IndexStock'
    days_past = 2
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'stk_index_corr_zz500', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '(-0.3,1]'
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-256:]
        stk_index_corr = data['stk_index_corr_zz500'].values[-256:]
        stk_index_corr_rank_mask = section_rank_np(stk_index_corr, pct=True) * 2 - 1
        n = 10
        temp = ts_sum(abs(ts_delta(stk_close, 1)), n)
        vi = abs(ts_delta(stk_close, n)) / replace_zero(temp)
        vidya = vi * stk_close + (1-vi) * ts_delay(stk_close, 1)
        factor_init = rolling_norm(vidya, 240)
        factor_raw = np.nansum(factor_init * stk_index_corr_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 2)
        return factor_mean[-1]
