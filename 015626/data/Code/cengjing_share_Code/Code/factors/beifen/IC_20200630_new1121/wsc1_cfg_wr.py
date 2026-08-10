import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc1_cfg_wr(FactorGeneratorComplex):
    def __init__(self):
        super(wsc1_cfg_wr, self).__init__(required_columns=['close_zz500', 'weight_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data):
        # mask
        stk_weight = data['weight_zz500']
        stk_weight_rank = 2 * stk_weight.rank(axis=1, pct=True) - 1

        # 计算长短两条均线包围的面积
        stk_close = data['close_zz500']
        close_ma_long = ts_mean(stk_close, 90)
        close_ma_short = ts_mean(stk_close, 15)
        factor_init = close_ma_short - close_ma_long
        factor_raw = (factor_init * stk_weight_rank).sum(axis=1)
        factor_mean = factor_raw
        factor = ts_rank(factor_mean, 1200)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
