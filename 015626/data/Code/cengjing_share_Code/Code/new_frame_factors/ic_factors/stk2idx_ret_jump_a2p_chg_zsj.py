import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

class stk2idx_ret_jump_a2p_chg_zsj(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close','adjfactor','amount']
    normalize_size = 2400
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        stk_close = data['close_preadj'][-120:]
        stk_amt = data['amount'][-120:]

        cut_line = stk_amt.median(axis=1)
        active_mask = stk_amt.subtract(cut_line, axis=0) >= 0
        inactive_mask = stk_amt.subtract(cut_line, axis=0) < 0

        stk_ret_short = stk_close/stk_close.shift(5) - 1
        stk_ret_long = stk_close/stk_close.shift(30) - 1
        stk_ret_jump = stk_ret_short - stk_ret_long

        score_raw = stk_ret_jump
        mask1 = active_mask
        mask2 = inactive_mask
        active_raw = score_raw[mask1].mean(axis=1)
        inactive_raw = score_raw[mask2].mean(axis=1)
        stk2idx_ret_jump_a2p_raw = (inactive_raw - active_raw)[-90:]
        factor = np.nanmean(stk2idx_ret_jump_a2p_raw[-10:]) - np.nanmean(stk2idx_ret_jump_a2p_raw)

        return factor