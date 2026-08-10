import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc3_cfg_vr(FactorGeneratorComplex):
    def __init__(self):
        super(wsc3_cfg_vr, self).__init__(required_columns=['close_zz500', 'close_spot', 'stk_volatility_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data):
        # mask
        volatility_mask = data['stk_volatility_zz500']
        volatility_rank_mask = 2 * volatility_mask.rank(axis=1, pct=True) - 1

        # 比较股票和指数涨幅大小，大则置1，小则置0
        stk_close = data['close_zz500']
        index_close = data['close_spot']
        index_return = index_close.pct_change(3, fill_method=None)
        stk_return = stk_close.pct_change(3, fill_method=None)
        return_difference = stk_return.sub(index_return, axis=0)
        return_difference[return_difference > 0] = 1
        return_difference[return_difference <= 0] = 0
        temp = ts_sum(return_difference, 90)
        temp[abs(temp)<1e-8] = np.nan
        factor_init = ts_sum(return_difference, 15) / temp
        factor_init = factor_init.replace([-np.inf, np.inf], np.nan)
        factor_raw = (factor_init * volatility_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 25)
        factor = ts_rank(factor_mean, 1200)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
