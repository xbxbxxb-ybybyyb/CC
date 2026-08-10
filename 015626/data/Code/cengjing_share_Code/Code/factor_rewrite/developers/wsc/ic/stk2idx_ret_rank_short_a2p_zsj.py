import numpy as np
import numpy.mask as ma
import bottleneck as bk
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class stk2idx_ret_rank_short_a2p_zsj(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'close', 'adjfactor']
    normalize_size = 2800
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-57:]
        stk_close = data['close_preadj'].values[-57:]
        stk_ret = ts_pct_change(stk_close, 1)
        stk_ret_rank_short = bk.move_rank(stk_ret, 30, 27, axis=0)
        cut_line = np.nanmedian(stk_amount, axis=1, keepdims=True)
        active_raw = ma.array(stk_ret_rank_short, mask=(stk_amount<cut_line))
        inactive_raw = ma.array(stk_ret_rank_short, mask=(stk_amount>=cut_line))
        score = np.nanmean(active_raw, axis=1) - np.nanmean(inactive_raw, axis=1)
        factor_raw = bk.move_mean(score, 25, int(25*0.9))
        return factor_raw[-1]