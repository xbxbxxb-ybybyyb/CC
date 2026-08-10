import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc1_cfg_vr(FactorGeneratorComplex):
    def __init__(self):
        super(wsc1_cfg_vr, self).__init__(required_columns=['close_zz500', 'stk_volatility_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data):
        # mask
        volatility_mask = data['stk_volatility_zz500']
        volatility_rank_mask = 2 * volatility_mask.rank(axis=1, pct=True) - 1
            
        # 计算长短两条均线包围的面积
        stk_close = data['close_zz500']
        close_ma_long = ts_mean(stk_close, 75)
        close_ma_short = ts_mean(stk_close, 10)
        factor_init = close_ma_short - close_ma_long

        factor_raw = (factor_init * volatility_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 5)
        factor = ts_rank(factor_mean, 900)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
