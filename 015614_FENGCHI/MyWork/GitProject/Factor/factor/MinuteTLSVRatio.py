import time
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.Util import array_coef, rolling_corr
from xfactor.FixUtil import minute_data_transform

'''
* 因子名 : MinuteTLSVRatio
* 因子功能描述 : 尾盘多空头平均成交量之比的排序
* 因子参数 : MinuteClose-分钟末端成交价格, MinuteVolume-分钟成交量
* 作者 : 沈天琦(shentq)
* 因子创建日期 : 2019.06.03
* 函数修改日期 : 尚未修改
* 修改人 ：尚未修改
* 修改原因 :  尚未修改
* 迁移作者：015625
* 迁移日期：2020.1.22
'''


class MinuteTLSVRatio(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute",
                   "FactorData.Basic_factor.volume_minute"]
    lag = 0

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        close_minute = single_database.depend_data["FactorData.Basic_factor.close_minute"]
        volume_minute = single_database.depend_data["FactorData.Basic_factor.volume_minute"]

        factor_values = self.minute(close_minute, volume_minute)
        ans = factor_values.iloc[-1]
        return ans

    def minute(self, MinuteClose, MinuteVolume):
        fmt = '%Y%m%d'

        date_list = np.unique(MinuteVolume.index.strftime(fmt))

        date = date_list[-1]

        df_factor = pd.DataFrame(index=[date], columns=MinuteVolume.columns)

        minute_close = MinuteClose.loc[date]
        minute_volume = MinuteVolume.loc[date]

        arr = minute_close.values / minute_close.shift(1).values - 1
        minute_close_return = pd.DataFrame(arr, index=minute_close.index,
                                           columns=minute_close.columns)

        mask1 = pd.DataFrame(minute_close_return.values > 0, index=minute_close_return.index,
                             columns=minute_close_return.columns)
        minute_long_volume_tail = minute_volume[-15:][mask1]

        mask2 = pd.DataFrame(minute_close_return.values < 0, index=minute_close_return.index,
                             columns=minute_close_return.columns)
        minute_short_volume_tail = minute_volume[-15:][mask2]

        arr = - minute_long_volume_tail.mean().values / minute_short_volume_tail.mean().values
        s = pd.Series(arr, index=minute_close_return.columns)

        df_factor.loc[date] = s.rank()

        return df_factor