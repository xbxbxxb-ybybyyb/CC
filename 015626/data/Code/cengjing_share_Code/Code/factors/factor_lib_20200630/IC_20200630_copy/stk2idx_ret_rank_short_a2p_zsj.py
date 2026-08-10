import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np
from functools import partial


def place_back_format(dat_mat, dat_orig):
    if isinstance(dat_orig, pd.DataFrame):
        dat_fmt = pd.DataFrame(dat_mat, index=dat_orig.index, columns=dat_orig.columns)
    elif isinstance(dat_orig, pd.Series):
        dat_fmt = pd.Series(dat_mat, index=dat_orig.index)
        dat_fmt.name = dat_orig.name
    else:
        dat_fmt = dat_mat
    return dat_fmt


def calc_ts_pct(ts_dat, roll_win=20, min_pct=1, force_range=False):
    min_win = int(min_pct * roll_win)
    ts_dat_pct_np = bk.move_rank(ts_dat, window=roll_win, min_count=min_win, axis=0)
    if force_range:
        ts_dat_pct_np = (ts_dat_pct_np + 1) / 2
    ts_dat_pct = place_back_format(ts_dat_pct_np, ts_dat)
    return ts_dat_pct


def calc_change_helper(score_raw, short_win, long_win, ts_pct_win, sign=1, min_pct=0.9):
    score_change_raw = sign * (
            score_raw.rolling(short_win, int(min_pct * short_win)).mean() - score_raw.rolling(long_win, int(
        min_pct * long_win)).mean())
    score_change = calc_ts_pct(score_change_raw, ts_pct_win, min_pct=min_pct)
    return score_change


def calc_std_helper(score_raw, std_win, ts_pct_win, min_pct=0.9):
    score_std_raw = score_raw.rolling(std_win, int(min_pct * std_win)).std()
    score_std = calc_ts_pct(score_std_raw, ts_pct_win)
    return score_std


def calc_ma_helper(score_raw, ma_win, ts_pct_win, min_pct=0.9):
    score_ma_raw = score_raw.rolling(ma_win, int(min_pct * ma_win)).mean()
    score_ma = calc_ts_pct(score_ma_raw, ts_pct_win, min_pct=min_pct)
    return score_ma


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


class stk2idx_ret_rank_short_a2p_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(stk2idx_ret_rank_short_a2p_zsj, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'weight_boolean_zz500'],
                                                             lookback_bars=2000)

    def on_bar(self, data):
        ## prep data
        stk_close = data['close_zz500']
        stk_amt = data['amount_zz500'][data['weight_boolean_zz500']]
 

        cut_line = stk_amt.median(axis=1)
        active_mask = stk_amt.subtract(cut_line, axis=0) >= 0
        inactive_mask = stk_amt.subtract(cut_line, axis=0) < 0

        # factor logic
        rank_win = 30
        stk_ret = stk_close/stk_close.shift(1) - 1
        stk_ret_rank_short = calc_ts_pct(stk_ret,rank_win)

        score_raw = stk_ret_rank_short
        mask1 = active_mask#up_mask_duration#up_mask#
        mask2 = inactive_mask#down_mask_duration#down_mask#inactive_mask
        active_raw = score_raw[mask1].mean(axis=1)
        inactive_raw = score_raw[mask2].mean(axis=1)
        score = active_raw - inactive_raw

        ma_win = 25
        ts_pct_win = 2800
        min_pct = 0.9
        stk2idx_ret_rank_short_a2p = calc_ma_helper(score,ma_win,ts_pct_win,min_pct)

        factor = stk2idx_ret_rank_short_a2p.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
