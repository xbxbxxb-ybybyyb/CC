import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
from xfactor.Util import array_coef

'''
* 迁移作者：015625
* 迁移日期：2020.1.13
'''


class Last30minReVolumeCorrMean5d(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.volume_adj_minute",
                   "FactorData.Basic_factor.amt_minute"]
    lag = 0
    minute_lag = 1
    reform_window = 5

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        volume_minute = single_database.depend_data["FactorData.Basic_factor.volume_adj_minute"]
        amt_minute = single_database.depend_data["FactorData.Basic_factor.amt_minute"]

        volume_minute = volume_minute.iloc[210:240:,:]
        amt_minute = amt_minute.iloc[210:240:,:]

        arr = amt_minute.values / volume_minute.values
        vwap = pd.DataFrame(arr, index=volume_minute.index, columns=volume_minute.columns)

        re = vwap.pct_change(1)

        cor = array_coef(re, volume_minute)
        return cor

    def reform(self, temp_result):
        ans = - temp_result.rolling(self.reform_window).mean()
        return ans