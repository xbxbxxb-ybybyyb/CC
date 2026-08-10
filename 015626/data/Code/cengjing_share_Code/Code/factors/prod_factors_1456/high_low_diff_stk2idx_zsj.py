import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np
from utils_zsj import *


class high_low_diff_stk2idx_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(high_low_diff_stk2idx_zsj, self).__init__(
            required_columns=['close_zz500', 'amount_zz500', 'high_zz500', 'low_zz500', 'open_zz500', 'weight_boolean_zz500'],
            lookback_bars=2000)

    def on_bar(self, data):
        ## prep data
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_high = data['high_zz500']
        stk_low = data['low_zz500']
        stk_open = data['open_zz500']
        stk_amt = data['amount_zz500']

        # factor logic
        # factor_name = 'high_low_diff_stk2idx'
        roll_win = 30
        ma_win = 30
        ts_pct_win = 2400
        min_pct = 0.9
        min_periods = int(0.5 * roll_win)
        high_open_diff = stk_high - stk_open
        open_low_diff = stk_open - stk_low
        high_low_diff_stk = high_open_diff.rolling(roll_win, min_periods).sum() - open_low_diff.rolling(roll_win,
                                                                                                        min_periods).sum()
        high_low_diff_stk2idx_raw = high_low_diff_stk[bool_mask].mean(axis=1)
        high_low_diff_stk2idx = calc_ma_helper(high_low_diff_stk2idx_raw, ma_win, ts_pct_win, min_pct)
        # ts_factor_quick(high_low_diff_stk2idx, price, factor_name, layers=5)

        factor = high_low_diff_stk2idx.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = ts_rank(factor, 200 * 4)
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
