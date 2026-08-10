from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

def calc_ts_pct(ts,ts_pct_win=20,min_pct=0.9,force_range=False):
    min_win = int(min_pct*ts_pct_win)
    ts_pct = bk.move_rank(ts,ts_pct_win,min_win,axis=0)
    if force_range:
        ts_pct = (ts_pct + 1)/2
    return ts_pct

def calc_ma_helper(score_raw,ma_win,ts_pct_win,min_pct=0.9):
    score_ma_raw = bk.move_mean(score_raw, ma_win, int(min_pct*ma_win), axis = 0)
    score_ma = calc_ts_pct(score_ma_raw,ts_pct_win)
    return score_ma


class csv_disp_chg_zsj(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['close', 'adjfactor'] 
    normalize_size = 1200
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        stk_close = data['close_preadj'][-1500:]
        stk_ret = (stk_close / stk_close.shift(1) - 1)

        csv_disp = stk_ret.std(axis=1)
        stk2idx_ret = stk_ret.mean(axis=1)
        csv_disp_sign_raw = csv_disp * np.sign(stk2idx_ret)
        
        csv_disp_sign = calc_ma_helper(csv_disp_sign_raw, 60, 1200)[-240:]
        flong = np.nanmean(csv_disp_sign)
        fshort = np.nanmean(csv_disp_sign[-20:])
        factor = fshort - flong
        
        return factor