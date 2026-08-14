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


class LowHighRetStdRatio(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.high_adj_minute",
                   "FactorData.Basic_factor.low_adj_minute"]
    lag = 0

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        high_minute = single_database.depend_data["FactorData.Basic_factor.high_adj_minute"]
        low_minute = single_database.depend_data["FactorData.Basic_factor.low_adj_minute"]

        high = high_minute.resample('10min').max().dropna(how='all', axis=0)  # resample成10分钟High
        low = low_minute.resample('10min').min().dropna(how='all', axis=0)  # resample成10分钟Low

        arr = high.values / high.shift(1).values - 1
        r_h = pd.DataFrame(arr, index=high.index, columns=high.columns)

        arr = low.values / low.shift(1).values - 1
        r_l = pd.DataFrame(arr, index=low.index, columns=low.columns)

        arr = r_l.std().values / r_h.std().values
        ans = pd.Series(arr, index=high_minute.columns)

        return ans
