import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
from help_functions_wsc import *



class wsc_mean_plus_std(FactorGenerator):
    def __init__(self):
        super(wsc_mean_plus_std, self).__init__(required_columns=['close_spot'],
                                                lookback_bars=2000)

    def on_bar(self, data):
        # 过去5分钟收益率的(均值+标准差*2)
        a = data['close_spot'].pct_change(5)
        b = a.rolling(30, min_periods=15).mean()
        c = a.rolling(30, min_periods=15).std()
        factor = b + 2 * c
        factor = factor.rolling(10).mean()
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = ts_rank(factor, 600)
        # factor[factor <= -0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
