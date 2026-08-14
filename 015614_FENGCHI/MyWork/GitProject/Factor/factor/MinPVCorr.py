import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.Util import array_coef
from xfactor.FixUtil import minute_data_transform, min_forward_adj

'''
* 迁移作者：015625
* 迁移日期：2020.1.14
'''


class MinPVCorr(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.close_adj_minute",
                   "FactorData.Basic_factor.volume_adj_minute"]
    lag = 0
    reform_window = 5

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        close_minute = single_database.depend_data["FactorData.Basic_factor.close_adj_minute"]
        volume_minute = single_database.depend_data["FactorData.Basic_factor.volume_adj_minute"]

        ans = array_coef(close_minute, volume_minute)
        return ans

    def reform(self, temp_result):
        def ewm(x):
            window = len(x)
            seq = [(1 - (2.0 / (window + 1))) ** (window - i) for i in range(1, window + 1)]
            weight = np.array(seq)
            weight_sum = np.sum(weight)
            return np.nansum(x * weight) / weight_sum

        def rolling_ewm(factor, window):
            factor = factor.rolling(window=window, min_periods=1).apply(lambda x: ewm(x))
            return factor

        ans = - temp_result.rolling(self.reform_window, 1).mean()
        return ans