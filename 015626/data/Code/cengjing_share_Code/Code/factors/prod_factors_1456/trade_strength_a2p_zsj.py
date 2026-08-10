import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np
from utils_zsj import *


class trade_strength_a2p_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(trade_strength_a2p_zsj, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'weight_boolean_zz500'],
                                                     lookback_bars=2000)

    def on_bar(self, data):
        ## prep data
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_amt = data['amount_zz500'][bool_mask]

        cut_line = stk_amt.median(axis=1)
        active_mask = stk_amt.subtract(cut_line, axis=0) >= 0
        inactive_mask = stk_amt.subtract(cut_line, axis=0) < 0

        # factor logic
        # factor_name = 'trade_strength_a2p'
        roll_win = 30
        ma_win = 30
        ts_pct_win = 4800
        min_pct = 0.9
        min_periods = int(min_pct * roll_win)
        abs_dis = np.abs(stk_close - stk_close.shift(1))
        stk_tot_dis = abs_dis.rolling(roll_win, min_periods).sum()
        stk_tot_dis[abs(stk_tot_dis)<1e-8] = np.nan
        stk_final_dis = stk_close - stk_close.shift(roll_win)
        stk_trade_strength = stk_final_dis / stk_tot_dis
        ts_active_raw = stk_trade_strength[active_mask].mean(axis=1)
        ts_inactive_raw = stk_trade_strength[inactive_mask].mean(axis=1)
        ts_a2p_raw = ts_active_raw - ts_inactive_raw
        trade_strength_a2p = calc_ma_helper(ts_a2p_raw, ma_win, ts_pct_win, min_pct)
        # ts_factor_quick(trade_strength_a2p, price, factor_name, layers=5)

        factor = trade_strength_a2p.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = ts_rank(factor, 200 * 4)
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
