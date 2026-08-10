import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
from help_functions_wsc import *



class wsc_return_comparison(FactorGenerator):
    def __init__(self):
        super(wsc_return_comparison, self).__init__(required_columns=['close_spot', 'close_spot_if'],
                                                    lookback_bars=2000)

    def on_bar(self, data):
        # 比较hs300指数和zz500指数过去三分钟收益率大小
        a = data['close_spot'].pct_change(3)
        b = data['close_spot_if'].pct_change(3)
        c = a - b
        c[c > 0] = 1
        c[c <= 0] = 0
        temp = c.rolling(180, min_periods=90).sum()
        temp[abs(temp)<1e-8] = np.nan
        factor = c.rolling(30, min_periods=15).sum() / temp
        factor = factor.rolling(10).mean()
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = ts_rank(factor, 600 * 2)
        # factor[factor <= -0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
