import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform

"""
* 因子名：MinuteRetSkewnessSharpe
* 因子功能描述：计算日内收益偏度的稳定性。
* 因子参数：MinuteClose
* 作者：姚逸凡
* 因子创建日期： 2019.1.15
* 函数修改日期： 尚未修改
* 修改人： 尚未修改
* 修改原因：尚未修改
* 迁移作者：015625
* 迁移日期：2020.1.10
"""


class MinuteRetSkewnessSharpe(BaseFactor):
    factor_type = "DAY"
    fix_times = ["1500"]
    depend_data = ["FactorData.Basic_factor.close_adj_minute"]
    lag = 0
    reform_window = 10

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        close_minute = single_database.depend_data["FactorData.Basic_factor.close_adj_minute"]

        close_minute = close_minute.resample('5T').last()

        arr = close_minute.values / close_minute.shift(1).values - 1
        ret_minute = pd.DataFrame(arr, index=close_minute.index, columns=close_minute.columns)
        skew = ret_minute.skew()

        if len(skew.dropna()) != 0:
            ans = skew
        else:
            ans = pd.Series(np.zeros(len(skew)), index=skew.index)

        return ans

    def reform(self, temp_result):
        temp_result_mean = temp_result.rolling(window=self.reform_window, min_periods=1).mean()
        temp_result_std = temp_result.rolling(window=self.reform_window, min_periods=1).std()

        arr = - abs(temp_result_mean.values / temp_result_std.values)
        result = pd.DataFrame(arr, index=temp_result.index, columns=temp_result.columns)
        return result
