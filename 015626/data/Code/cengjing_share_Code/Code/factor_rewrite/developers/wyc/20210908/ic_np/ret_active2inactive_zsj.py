import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

class ret_active2inactive_zsj(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close','adjfactor','amount']
    normalize_size = 1200
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        stk_close = data['close_preadj'][-181:]
        stk_amt = data['amount'][-181:]
        stk_ret = (stk_close / stk_close.shift(1) - 1)
        cut_line = stk_amt.median(axis=1)
        active_mask = stk_amt.subtract(cut_line, axis=0) >= 0
        inactive_mask = stk_amt.subtract(cut_line, axis=0) < 0
        ret_active_raw = stk_ret[active_mask].mean(axis=1)
        ret_inactive_raw = stk_ret[inactive_mask].mean(axis=1)
        ret_active2inactive_raw = (ret_active_raw - ret_inactive_raw).values[-180:]
        factor = np.nanmean(ret_active2inactive_raw)
        return factor