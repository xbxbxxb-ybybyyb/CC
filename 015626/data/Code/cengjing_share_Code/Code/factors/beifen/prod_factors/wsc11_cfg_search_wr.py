import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc11_cfg_search_wr(FactorGeneratorComplex):
    def __init__(self):
        super(wsc11_cfg_search_wr, self).__init__(required_columns=['close_zz500', 'weight_zz500'],
                                                  lookback_bars=2000)

    def on_bar(self, data):
        # mask
        stk_weight = data['weight_zz500']
        stk_weight_rank = 2 * stk_weight.rank(axis=1, pct=True) - 1

        # 算子搜索
        stk_close = data['close_zz500']
        stk_close_delta = ts_delta(stk_close, 15)
        factor_init = ts_max(stk_close_delta, 20)

        factor_raw = (factor_init * stk_weight_rank).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 1)
        factor = ts_rank(factor_mean, 1200)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.9] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
