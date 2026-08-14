import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform

"""
    * 因子名：MinPreVolRet
    * 因子功能描述：计算前日收益率加权的成交量占比，是一种反转因子；当收益率成家量双双到达顶峰，是一种超买状态，表现负收益
    * 因子参数：  MinuteClose, MinuteVolume
    * 作者：肖倩
    * 因子创建日期： 2019.7.1
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
"""

class MinPreVolRet(BaseFactor):
    factor_type = 'FIX'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.close_adj_minute',
                   'FactorData.Basic_factor.volume_minute']
    lag = 0
    minute_lag = 1
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_adj_minute']
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']

        fmt = '%Y%m%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))
        pre_date = date_list[-2]
        close_df = MinuteClose.loc[pre_date]
        volume_df = MinuteVolume.loc[pre_date]
        ret = pd.DataFrame(close_df.values / close_df.shift(1).values - 1, index=close_df.index,
                           columns=close_df.columns)

        result = pd.DataFrame(ret.values * volume_df.values / volume_df.sum().values,
                              index=ret.index,
                              columns=ret.columns).mean()
        return result

    def reform(self, temp_result):
        ans = - temp_result.rolling(window=self.reform_window, min_periods=1).apply(lambda x: self.ewm(x))
        return ans

    def ewm(self, x):
        window = len(x)
        seq = [(1-(2.0/(window+1))) ** (window-i) for i in range(1, window + 1)]
        weight = np.array(seq)
        weight_sum = np.sum(weight)
        return np.nansum(x * weight) / weight_sum

