import pandas as pd
import numpy as np
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc_cfg11(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_cfg11, self).__init__(required_columns=['close_zz500', 'weight_zz500'],
                                        lookback_bars=2000)

    def on_bar(self, data):
        # 收益率的均值与标准差之和
        close = data['close_zz500']
        ret = close.pct_change(5, fill_method=None)
        ret_mean = ts_mean(ret, 20)
        ret_std = ts_std(ret, 20)
        factor = ret_mean + 1 * ret_std
        # factor = factor.rolling(10, min_periods=5).mean()
        # factor = factor.sum(axis=1)

        factor = (factor * data['weight_zz500']).sum(axis=1)
        # factor = ((ret_long * data['weight_zz500']).sum(axis=1)) / weight_long.sum(axis=1) - (ret * data['weight_zz500']).sum(axis=1)
        #factor = factor.rolling(15, min_periods=2).mean()
        factor = factor.to_frame()   
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = ts_rank(factor, 1200)
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        factor[factor<=-0.5] = 0
        #factor[factor>=0.5] = np.nan
        return factor