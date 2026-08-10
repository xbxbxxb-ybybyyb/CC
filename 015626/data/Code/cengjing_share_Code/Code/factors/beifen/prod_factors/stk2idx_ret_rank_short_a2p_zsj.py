import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np
from functools import partial
from utils_zsj import *


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
        stk_close[abs(stk_close) < 1e-8] = np.nan
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
