import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np
from functools import partial
from utils_zsj import *


class stk2idx_amt_ret_corr_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(stk2idx_amt_ret_corr_zsj, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'weight_boolean_zz500'],
                                                     lookback_bars=2000)

    def on_bar(self, data):
        ## prep data
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_amt = data['amount_zz500']
        stk_close[abs(stk_close) < 1e-8] = np.nan
        # factor logic
        stk_amt_change = (stk_amt - stk_amt.shift(1))[bool_mask]
        stk_ret = (stk_close/stk_close.shift(1) - 1)[bool_mask]
        amt_ret_corr_raw = stk_amt_change.corrwith(stk_ret,axis=1)
        ma_win = 30
        ts_pct_win = 1200
        min_pct = 0.9
        stk2idx_amt_ret_corr = calc_ma_helper(amt_ret_corr_raw,ma_win,ts_pct_win,min_pct)

        factor = stk2idx_amt_ret_corr.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
