import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.Util import array_coef
from xfactor.FixUtil import minute_data_transform, min_forward_adj

'''
* 迁移作者：015625
* 迁移日期：2020.1.14
'''


class MinExtremRet(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.close_adj_minute",
                   "FactorData.Basic_factor.volume_adj_minute"]
    lag = 0
    minute_lag = 1

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        close_minute = single_database.depend_data["FactorData.Basic_factor.close_adj_minute"]
        volume_minute = single_database.depend_data["FactorData.Basic_factor.volume_adj_minute"]

        arr = close_minute.values / close_minute.shift(1).values - 1
        return_df = pd.DataFrame(arr, index=close_minute.index, columns=close_minute.columns)

        arr = volume_minute.values > volume_minute.mean().values + 2 * volume_minute.std().values
        flag = pd.DataFrame(arr, index=volume_minute.index, columns=volume_minute.columns)

        result = - return_df[flag].sum()
        return result
