import pandas as pd
import numpy as np
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc_cfg6(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_cfg6, self).__init__(required_columns=['close_zz500', 'volume_zz500', 'weight_zz500', 'weight_boolean_zz500'],
                                       lookback_bars=2000)

    def on_bar(self, data):
        # 选取截面上成交量最大的前10%的股票，计算它们的加权平均收益率（权重为weight）
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_volume = data['volume_zz500'][bool_mask]
        stk_ret = stk_close.pct_change(5, fill_method=None)
        stk_volume_long = stk_volume.gt(stk_volume.quantile(0.9, axis=1), axis=0)
        factor = stk_ret[stk_volume_long]#.rolling(30, min_periods=20).mean()
        # factor = stk_ret.rolling(30*2, min_periods=15).cov(stk_amt)
        factor = (factor * data['weight_zz500']).sum(axis=1)
        factor = ts_mean(factor, 30)

        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = ts_rank(factor, 1200)
        # factor[factor<=-0.5] = np.nan
        #factor[factor>=0.5] = np.nan
        return factor
