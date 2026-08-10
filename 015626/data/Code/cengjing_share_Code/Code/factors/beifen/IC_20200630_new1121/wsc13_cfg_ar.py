import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc13_cfg_ar(FactorGeneratorComplex):
    def __init__(self):
        super(wsc13_cfg_ar, self).__init__(required_columns=['weight_zz500', 'volume_zz500', 'amount_zz500', 'weight_boolean_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data):
        # mask
        stk_amount = data['amount_zz500']
        weight_true = data['weight_boolean_zz500']
        amount_mask = stk_amount[weight_true]
        amount_rank_mask = 2 * amount_mask.rank(axis=1, pct=True) - 1

        # 东方金工20191029，用区间内的vwap和vwap均值之间的偏差度量买卖压力
        stk_volume = data['volume_zz500']
        stk_vwap = stk_amount / stk_volume
        vwap_ma = ts_mean(stk_vwap, 45)
        amount_ma = ts_mean(stk_amount, 45)
        volume_ma = ts_mean(stk_volume, 45)
        volume_ma[abs(volume_ma)<1e-8] = np.nan
        temp = amount_ma / volume_ma
        temp[abs(temp)<1e-8] = np.nan
        apb = vwap_ma / temp
        factor_init = -np.log(apb)

        factor_raw = (factor_init * amount_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 10)
        factor = ts_rank(factor_mean, 2000)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.9] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
