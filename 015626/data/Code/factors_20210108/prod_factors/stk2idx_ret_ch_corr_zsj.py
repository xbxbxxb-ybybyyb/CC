import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np
from functools import partial
from utils_zsj import *


class stk2idx_ret_ch_corr_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(stk2idx_ret_ch_corr_zsj, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'high_zz500', 'weight_boolean_zz500'],
                                                     lookback_bars=2000)

    def on_bar(self, data):
        ## prep data
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_amt = data['amount_zz500']

        # factor logic
        stk_high = data['high_zz500']
        stk_close[abs(stk_close) < 1e-8] = np.nan
        stk_high[abs(stk_high) < 1e-8] = np.nan
        stk_ret_close = stk_close/stk_close.shift(1) - 1
        stk_ret_high = stk_high/stk_high.shift(1) - 1
        ret_close_high_corr_raw = stk_ret_close[bool_mask].corrwith(stk_ret_high[bool_mask],axis=1)
        ma_win = 30
        ts_pct_win = 1200
        min_pct = 0.9
        stk2idx_ret_ch_corr = calc_ma_helper(ret_close_high_corr_raw,ma_win,ts_pct_win,min_pct)

        factor = stk2idx_ret_ch_corr.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
