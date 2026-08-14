import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.Util import array_coef
from xfactor.FixUtil import minute_data_transform, min_forward_adj

'''
* 因子名：MinCorrVolumeRetUp_1
* 因子功能描述：当日截至13:00前成交量和上行收益率的相关性。再与前五日该值的均值求和。
该值越大，说明前期成交量放大伴随着更高的收益率幅度，可能是大单操作、信息泄露更显著，后市收益空间有限。
* 因子参数：[MinuteClose]: 分钟收盘价
           [MinuteVolume]: 分钟成交量
* 作者：周璇
* 因子创建日期：2019.6.26
* 函数修改日期：尚未修改
* 修改人：尚未修改
* 修改原因：尚未修改
* 迁移作者：015625
* 迁移日期：2020.1.14
'''


class MinCorrVolumeRetUp_1(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.close_adj_minute",
                   "FactorData.Basic_factor.volume_adj_minute"]
    lag = 0
    minute_lag = 5

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        close_minute = single_database.depend_data["FactorData.Basic_factor.close_adj_minute"]
        volume_minute = single_database.depend_data["FactorData.Basic_factor.volume_adj_minute"]

        fmt = '%Y%m%d'
        date_list = sorted(np.unique(close_minute.index.strftime(fmt)))
        MinCorrVolumeRetUp = pd.DataFrame(index=date_list, columns=close_minute.columns)

        for date in date_list:
            close = close_minute.loc[date]

            arr = close.values / close.shift(1).values - 1
            r = pd.DataFrame(arr, index=close.index, columns=close.columns)

            volume = volume_minute.loc[date]

            arr = r.values > 0
            df = pd.DataFrame(arr, index=r.index, columns=r.columns)

            MinCorrVolumeRetUp.loc[date] = array_coef(volume[df], r[df])

        arr = - (MinCorrVolumeRetUp.iloc[-1].values + MinCorrVolumeRetUp.iloc[:-1].mean().values)
        ans = pd.Series(arr, index=MinCorrVolumeRetUp.columns)
        return ans
