import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np


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


class high_low_diff_stk2idx_zsj_if(FactorGeneratorComplex):
    def __init__(self):
        super(high_low_diff_stk2idx_zsj_if, self).__init__(
            required_columns=['close_hs300', 'amount_hs300', 'high_hs300', 'low_hs300', 'open_hs300', 'weight_boolean_hs300'],
            lookback_bars=3000)

    def on_bar(self, data):
        ## prep data
        stk_close = data['close_hs300']
        stk_high = data['high_hs300']
        stk_low = data['low_hs300']
        stk_open = data['open_hs300']
        stk_amount = data['amount_hs300']
        bool_mask = data['weight_boolean_hs300']

        # factor logic
        # factor_name = 'high_low_diff_stk2idx'
        roll_win = 45
        ma_win = 15
        ts_pct_win = 3000
        min_pct = 0.9
        min_periods = int(0.5 * roll_win)
        high_open_diff = stk_high - stk_open
        open_low_diff = stk_open - stk_low
        high_low_diff_stk = high_open_diff.rolling(roll_win, min_periods).sum() - open_low_diff.rolling(roll_win,
                                                                                                        min_periods).sum()
        high_low_diff_stk2idx_raw = high_low_diff_stk[bool_mask].mean(axis=1)
        high_low_diff_stk2idx = calc_ma_helper(high_low_diff_stk2idx_raw, ma_win, ts_pct_win, min_pct)

        factor = high_low_diff_stk2idx.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
