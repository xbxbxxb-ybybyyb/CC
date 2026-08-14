import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform

'''
* 因子名称： LowHighRetStdRatio_13h
* 描述： Low收益率的标准差 / High收益率的标准差
* 因子逻辑： High变化率相比Low的更稳定，说明多头力量相比空头力量更稳定
* 因子参数： 分钟数据的最高价、最低价
* 作者： 何丰敬
* 日期： 2019.10.21
* 函数修改日期: 尚未修改
* 修改人： 尚未修改
* 修改原因： 尚未修改
* 迁移作者：015625
* 迁移日期：2020.1.13
'''


class LowHighStdRatio(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.high_adj_minute",
                   "FactorData.Basic_factor.low_adj_minute"]
    lag = 0
    minute_lag = 1

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        high_minute = single_database.depend_data["FactorData.Basic_factor.high_adj_minute"]
        low_minute = single_database.depend_data["FactorData.Basic_factor.low_adj_minute"]

        high = high_minute.iloc[-60:].std()  # 最近60分钟High的标准差
        low = low_minute.iloc[-60:].std()  # 最近60分钟Low的标准差

        arr = low.values / high.values
        ans = pd.Series(arr, index=high.index)
        ans = ans.replace(np.inf, np.nan)

        return ans