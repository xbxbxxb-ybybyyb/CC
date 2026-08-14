import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.Util import array_coef
from xfactor.FixUtil import minute_data_transform

'''
* 因子名：MinCorrVolumePrice_1
* 因子功能描述：当日截至13:00分钟收盘价和成交量的相关性与前5天量价相关性的均值取平均。
相关性越低，说明前期缩量上涨，放量下跌，短期内下跌量能散尽，后市补涨可能性更高，当日数据量较少，前5日可提供更多信息量。
* 因子参数：[MinuteClose]: 分钟收盘价
           [MinuteVolume]: 分钟成交量
* 作者：周璇
* 因子创建日期：2019.6.25
* 函数修改日期：尚未修改
* 修改人：尚未修改
* 修改原因：尚未修改
* 迁移作者：015625
* 迁移日期：2020.1.14
'''


class MinCorrVolumePrice_1(BaseFactor):
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
        datelist = sorted(np.unique(close_minute.index.strftime(fmt)))
        CorrVolumePrice = pd.DataFrame(index=datelist, columns=close_minute.columns)
        for date in datelist:
            close = close_minute.loc[date]
            volume = volume_minute.loc[date]
            CorrVolumePrice.loc[date] = array_coef(volume, close)

        arr = - (CorrVolumePrice.iloc[:-1].mean(axis=0).values + CorrVolumePrice.iloc[-1].values)
        result = pd.Series(arr, index=CorrVolumePrice.columns)
        return result
