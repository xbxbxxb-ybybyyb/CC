import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np
from functools import partial
from utils_zsj import *


class stk2idx_amt_chg_u2d_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(stk2idx_amt_chg_u2d_zsj, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'weight_boolean_zz500'],
                                                     lookback_bars=2000)

    def on_bar(self, data):
        ## prep data
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_amt = data['amount_zz500']
        stk_close[abs(stk_close) < 1e-8] = np.nan
        stk_ret = (stk_close / stk_close.shift(1) - 1)[bool_mask]
        up_mask = stk_ret > 0
        down_mask = stk_ret < 0

        # factor logic
        stk_amt_chg = stk_amt - stk_amt.shift(1)
        score_raw = stk_amt_chg
        mask1 = up_mask
        mask2 = down_mask
        active_raw = score_raw[mask1].mean(axis=1)
        inactive_raw = score_raw[mask2].mean(axis=1)
        score = active_raw - inactive_raw

        ma_win = 60
        ts_pct_win = 1200
        min_pct = 0.9
        stk2idx_amt_chg_u2d = calc_ma_helper(score,ma_win,ts_pct_win,min_pct)

        factor = stk2idx_amt_chg_u2d.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
