import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np
from utils_zsj import *


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
