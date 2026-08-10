import numpy as np
import numpy.ma as ma
import bottleneck as bk
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import *


class trade_strength_a2p_zsj_IH(FutureFactor):
    data_type = 'IndexStock'
    days_past = 21
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'close', 'adjfactor']
    normalize_size = 800
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-4861:]
        stk_close = data['close_preadj'].values[-4861:]
        roll_win = 30
        min_pct = 0.9        
        min_periods = int(min_pct * roll_win)
        ma_win = 30
        ts_pct_win = 4800
        cut_line = np.nanmedian(stk_amount, axis=1, keepdims=True)
        abs_dis = np.abs(ts_delta(stk_close, 1))
        stk_tot_dis = bk.move_sum(abs_dis, roll_win, min_periods, axis=0)
        stk_final_dis = ts_delta(stk_close, roll_win)
        stk_trade_strength = stk_final_dis / replace_zero(stk_tot_dis)
        ts_active_raw = ma.array(stk_trade_strength, mask=(stk_amount<cut_line))
        ts_inactive_raw = ma.array(stk_trade_strength, mask=(stk_amount>=cut_line))
        ts_a2p_raw = np.nanmean(ts_active_raw, axis=1) - np.nanmean(ts_inactive_raw, axis=1)
        ts_pct_np = bk.move_mean(ts_a2p_raw, ma_win, int(ma_win*min_pct), axis=0)
        factor_raw = bk.move_rank(ts_pct_np, ts_pct_win, int(ts_pct_win*min_pct), axis=0)
        return factor_raw[-1]
