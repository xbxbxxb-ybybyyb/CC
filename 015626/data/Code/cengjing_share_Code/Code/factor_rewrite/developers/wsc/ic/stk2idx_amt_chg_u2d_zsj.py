import numpy as np
import numpy.mask as ma
import bottleneck as bk
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class stk2idx_amt_chg_u2d_zsj(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'close', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-62:]
        stk_close = data['close_preadj'].values[-62:]
        stk_amt_chg = ts_delta(stk_amount, 1)
        stk_ret = ts_pct_change(stk_close, 1)
        active_raw = ma.array(stk_amt_chg, mask=(stk_ret<=0))
        inactive_raw = ma.array(stk_amt_chg, mask=(stk_ret>=0))
        score = np.nanmean(active_raw, axis=1) - np.nanmean(inactive_raw, axis=1)
        factor_raw = bk.move_mean(score, 60, 54)
        return factor_raw[-1]