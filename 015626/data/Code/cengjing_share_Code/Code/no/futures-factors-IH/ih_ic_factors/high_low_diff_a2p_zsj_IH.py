import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

class high_low_diff_a2p_zsj_IH(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 11
    data_dict = dict()
    data_dict['Stock'] = ['close','adjfactor','amount','open','high','low']
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

        cut_line = stk_amt.median(axis=1)
        active_mask = stk_amt.subtract(cut_line, axis=0) >= 0
        inactive_mask = stk_amt.subtract(cut_line, axis=0) < 0

        high_open_diff = stk_high - stk_open
        open_low_diff = stk_open - stk_low
        high_low_diff_stk = high_open_diff.rolling(30, 27).sum() - open_low_diff.rolling(30, 27).sum()
        high_low_diff_active_raw = high_low_diff_stk[active_mask].mean(axis=1)[-2430:]
        high_low_diff_inactive_raw = high_low_diff_stk[inactive_mask].mean(axis=1)[-2430:]
        high_low_diff_a2p_raw = (high_low_diff_active_raw - high_low_diff_inactive_raw).values
        ma = bk.move_mean(high_low_diff_a2p_raw, 30, min_count=27, axis = 0)[-2400:]
        ts_dat_pct_np = bk.move_rank(ma, window=2400, min_count=2160, axis=0)
        factor = (ts_dat_pct_np[-1] + 1) / 2
        return factor