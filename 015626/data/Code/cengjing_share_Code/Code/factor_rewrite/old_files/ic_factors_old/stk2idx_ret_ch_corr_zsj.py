import numpy as np
import bottleneck as bk
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class stk2idx_ret_ch_corr_zsj(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'close', 'adjfactor', 'high']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-32:]
        stk_close = data['close_preadj'].values[-32:]
        stk_high = data['high_preadj'].values[-32:]
        stk_ret_high = ts_pct_change(stk_high, 1)
        stk_ret_close = ts_pct_change(stk_close, 1)
        ret_close_high_corr_raw = pairwise_corr_np(stk_ret_high, stk_ret_close, axis=1)
        factor_raw = bk.move_mean(ret_close_high_corr_raw, 30, 27)
        return factor_raw[-1]
