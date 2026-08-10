from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class high_low_diff_stk2idx_zsj(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 11
    data_dict = dict()
    data_dict['Stock'] = ['close', 'open', 'high', 'low', 'amount', 'adjfactor'] 
    normalize_size = 800
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        stk_close = data['close_preadj'][-2460:]
        stk_high = data['high_preadj'][-2460:]
        stk_low = data['low_preadj'][-2460:]
        stk_open = data['open_preadj'][-2460:]
        stk_amt = data['amount'][-2460:]

        high_open_diff = stk_high - stk_open
        open_low_diff = stk_open - stk_low
        high_low_diff_stk = bk.move_sum(high_open_diff, 30, 15, axis = 0) - bk.move_sum(open_low_diff, 30, 15, axis = 0)
        high_low_diff_stk2idx_raw = np.nanmean(high_low_diff_stk, axis=1)[-2430:]
        
        mma = bk.move_mean(high_low_diff_stk2idx_raw, 30, 27, axis = 0)[-2400:]
        factor = bk.move_rank(mma, 2400, 2160, axis=0)[-1]

        return factor
