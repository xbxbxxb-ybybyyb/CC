import time
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.Util import array_coef, rolling_corr
from xfactor.FixUtil import minute_data_transform

'''
* 因子名：Minute30CloseVolumeCorr
* 因子功能描述：
- 计算公式
    a = rank(close30min / delay(close30min) - 1)
    b = rank(volume30min / delay(volume30min) - 1)
    ans = corr(a, b, 8*5)
- 编写逻辑
    将每天的240个分钟close和volume，以半小时为时间区间resample成8个30分钟线。
    对过去5天共40个数据点的close和volume的增长率分别进行横截面排名，对两者的排名计算相关性取相反数。
* 因子参数： close_badj, volume, close_adj_minute, volume_minute
* 作者：王海洋
* 因子创建时间： 2019.02.24
* 函数修改日期：尚未修改
* 修改人：尚未修改
* 修改原因：尚未修改 
'''


class Minute30CloseVolumeCorr(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_adj_minute",
                   "FactorData.Basic_factor.volume_minute"]
    minute_lag = 5

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        close_minute = single_database.depend_data["FactorData.Basic_factor.close_adj_minute"]
        volume_minute = single_database.depend_data["FactorData.Basic_factor.volume_minute"]

        close_30min = close_minute.resample('30T').last().dropna(how='all')
        volume_30min = volume_minute.resample('30T').mean().dropna(how='all')

        close_30min_ret = pd.DataFrame(close_30min.values / close_30min.shift(1).values - 1,
                                       index=close_30min.index, columns=close_30min.columns)
        volume_30min_ret = pd.DataFrame(volume_30min.values / volume_30min.shift(1).values - 1,
                                        index=volume_30min.index, columns=volume_30min.columns)

        a = close_30min_ret.rank(axis=1)
        b = volume_30min_ret.rank(axis=1)

        ans = - array_coef(a, b)

        return ans






