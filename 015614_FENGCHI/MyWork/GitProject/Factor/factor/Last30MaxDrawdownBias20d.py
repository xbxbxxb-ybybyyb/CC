import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform

'''
* 迁移作者：015625
* 迁移日期：2020.1.13
'''


class Last30MaxDrawdownBias20d(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.volume_adj_minute",
                   "FactorData.Basic_factor.amt_minute"]
    lag = 0
    minute_lag = 1
    reform_window = 20

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        volume_minute = single_database.depend_data["FactorData.Basic_factor.volume_adj_minute"]
        amt_minute = single_database.depend_data["FactorData.Basic_factor.amt_minute"]

        arr = amt_minute.values / volume_minute.values
        vwap = pd.DataFrame(arr, index=volume_minute.index, columns=volume_minute.columns).iloc[-30:, :]

        max2here = vwap.expanding().max()

        arr = vwap.values / max2here.values - 1
        dd2here = pd.DataFrame(arr, index=vwap.index, columns=vwap.columns)
        ans = dd2here.min()

        return ans

    def reform(self, temp_result):
        arr = (temp_result.values - temp_result.rolling(self.reform_window).mean().values) / \
              temp_result.rolling(self.reform_window).std()
        ans = pd.DataFrame(arr, index=temp_result.index, columns=temp_result.columns)
        return ans