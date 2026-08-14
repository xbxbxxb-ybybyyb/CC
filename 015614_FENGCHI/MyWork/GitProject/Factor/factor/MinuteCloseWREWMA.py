import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform

"""
* 因子名 : MinuteCloseWREWMA
* 因子功能描述 : 计算分钟级高频数据因子，捕捉尾盘WR指标的EWMA，即(High-Close)/(High-Low)
* 因子参数 : *
* 函数返回值 : MinuteCloseWREWMA
* 作者 : 孙海平
* 因子创建日期 : 2019.4.16
* 函数修改日期 : 尚未修改
* 修改人 ：尚未修改
* 修改原因 :  尚未修改
* 版本 : 1.0
* 历史版本 : 无
* 迁移作者：015625
* 迁移日期：2020.1.10
"""


class MinuteCloseWREWMA(BaseFactor):
    factor_type = "DAY"
    fix_times = ["1500"]
    depend_data = ["FactorData.Basic_factor.close_adj_minute",
                   "FactorData.Basic_factor.high_adj_minute",
                   "FactorData.Basic_factor.low_adj_minute"]
    lag = 0
    reform_window = 5

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        close_minute = single_database.depend_data["FactorData.Basic_factor.close_adj_minute"]
        high_minute = single_database.depend_data["FactorData.Basic_factor.high_adj_minute"]
        low_minute = single_database.depend_data["FactorData.Basic_factor.low_adj_minute"]

        n = 30
        high = high_minute.iloc[-n:].max()
        low = low_minute.iloc[-n:].min()
        close = close_minute.iloc[-1]

        arr = (high.values - close.values) / (high.values - low.values)
        wr1 = pd.Series(arr, index=close_minute.columns)
        wr1[np.isinf(wr1)] = 0

        return wr1

    def reform(self, temp_result):
        def rolling_ewm(df, n=5):
            seq = [(1 - (2.0 / (n + 1))) ** (n - i) for i in range(1, n + 1)]
            weight = np.array(seq)
            weight_sum = np.sum(weight)
            return df.rolling(window=n).apply(lambda x: np.sum(x * weight) / weight_sum)

        ans = rolling_ewm(temp_result, self.reform_window)
        return ans