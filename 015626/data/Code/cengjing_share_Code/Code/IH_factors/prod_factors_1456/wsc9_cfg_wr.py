import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc9_cfg_wr(FactorGeneratorComplex):
    def __init__(self):
        super(wsc9_cfg_wr, self).__init__(required_columns=['close_zz500', 'weight_zz500', 'open_zz500', 'volume_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data):
        # mask
        stk_weight = data['weight_zz500']
        stk_weight_rank = 2 * stk_weight.rank(axis=1, pct=True) - 1

        # 假设持仓30分钟，min_30_earning表示那一分钟这笔持仓的盈亏
        stk_close = data['close_zz500']
        stk_open = data['open_zz500']
        stk_volume = data['volume_zz500']
        min_30_earning = (stk_close - stk_open.shift(30)) * stk_volume
        factor_init = min_30_earning

        factor_raw = (factor_init * stk_weight_rank).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 20)
        factor = ts_rank(factor_mean, 1200)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.9] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
