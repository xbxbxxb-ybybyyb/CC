import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.Util import array_coef
from xfactor.FixUtil import minute_data_transform, min_forward_adj

'''
* 因子名：MinDirectedVol
* 因子功能描述：计算当日收益率加权的成交量占比，是一种反转因子；当收益率成家量双双到达顶峰，是一种超买状态，表现负收益
* 因子参数：  MinuteClose, MinuteVolume
* 作者：肖倩
* 因子创建日期： 2019.7.1
* 函数修改日期： 尚未修改
* 修改人： 尚未修改
* 修改原因：尚未修改
* 迁移作者：015625
* 迁移日期：2020.1.14
'''


class MinDirectedVol(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.close_adj_minute",
                   "FactorData.Basic_factor.volume_adj_minute"]

    lag = 0

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        close_minute = single_database.depend_data["FactorData.Basic_factor.close_adj_minute"]
        volume_minute = single_database.depend_data["FactorData.Basic_factor.volume_adj_minute"]

        arr = close_minute.values / close_minute.shift(1).values - 1
        ret = pd.DataFrame(arr, index=close_minute.index, columns=close_minute.columns)

        arr = ret.values * volume_minute.values / volume_minute.sum().values
        df = pd.DataFrame(arr, index=volume_minute.index, columns=volume_minute.columns)
        result = - df.std()
        return result
