import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform

"""
* 因子名：MinuteRetVolMultSkew
* 因子功能描述：计算最后两小时收益与成交量占比之积之20日偏度。
* 因子参数：MinuteClose
* 作者：姚逸凡
* 因子创建日期： 2019.1.15
* 函数修改日期： 尚未修改
* 修改人： 尚未修改
* 修改原因：尚未修改
"""


class MinuteRetVolMultSkew(BaseFactor):
    factor_type = "DAY"
    fix_times = ["1500"]
    depend_data = ["FactorData.Basic_factor.close_adj_minute",
                   "FactorData.Basic_factor.volume_adj_minute"]
    lag = 0
    reform_window = 20

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        close_minute = single_database.depend_data["FactorData.Basic_factor.close_adj_minute"]
        volume_minute = single_database.depend_data["FactorData.Basic_factor.volume_adj_minute"]

        n = 120

        arr = close_minute.iloc[-1].values / close_minute.iloc[-n].values - 1
        ret = pd.Series(arr, index=close_minute.columns)

        arr = volume_minute[-n:].sum(axis=0).values / volume_minute.sum(axis=0).values
        vol_last = pd.Series(arr, index=close_minute.columns)

        if len(vol_last.dropna()) != 0:
            ans = vol_last
        else:
            ans = pd.Series(np.ones(len(vol_last)), index=vol_last.index)

        arr = - ret.values * ans.values
        ans_final = pd.Series(arr, index=ans.index)
        return ans_final

    def reform(self, temp_result):
        temp_result = temp_result.rolling(self.reform_window).skew()
        return temp_result