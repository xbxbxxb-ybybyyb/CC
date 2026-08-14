import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.Util import array_coef
from xfactor.FixUtil import minute_data_transform, min_forward_adj

'''
* 因子名：MinPre5mSkew
* 因子功能描述：昨日下午盘5分钟k线收益率偏度的5日加权平均
* 因子参数：  MinuteClose
* 作者：肖倩
* 因子创建日期： 2019.06.23
* 函数修改日期： 尚未修改
* 修改人： 尚未修改
* 修改原因：尚未修改
* 迁移作者：015625
* 迁移日期：2020.1.14
'''


class MinPre5mSkew(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.close_adj_minute"]
    lag = 0
    minute_lag = 2
    reform_window = 5

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        close_minute = single_database.depend_data["FactorData.Basic_factor.close_adj_minute"]

        fmt = '%Y%m%d'
        date_list = np.unique(close_minute.index.strftime(fmt))
        pre_date = date_list[-2]
        close_df = close_minute.loc[pre_date]

        arr = close_df.values / close_df.shift(5).values
        return_df = pd.DataFrame(arr, index=close_df.index, columns=close_df.columns).iloc[-120:]

        sk = return_df.skew()
        return sk

    def reform(self, temp_result):
        def ewm(x):
            window = len(x)
            seq = [(1 - (2.0 / (window + 1))) ** (window - i) for i in range(1, window + 1)]
            weight = np.array(seq)
            weight_sum = np.sum(weight)
            return np.nansum(x * weight) / weight_sum
        ans = - temp_result.rolling(window=self.reform_window, min_periods=1).apply(lambda x: ewm(x))
        return ans
