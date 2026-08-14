import time
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.Util import array_coef, rolling_corr
from xfactor.FixUtil import minute_data_transform

'''
* 因子名：TemporalVolumePriceCorr
* 因子功能描述：量价变化在时序上相对强度的相关性
* 因子参数： close_badj, volume, close_adj_minute, volume_minute
* 作者：王海洋
* 因子创建时间： 2019.02.09
* 函数修改日期：尚未修改
* 修改人：尚未修改
* 修改原因：尚未修改 
'''


class TemporalVolumePriceCorr(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.close_badj",
                   "FactorData.Basic_factor.volume",
                   "FactorData.Basic_factor.close_adj_minute",
                   "FactorData.Basic_factor.volume_minute"]
    lag = 10
    minute_lag = 0

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        close = single_database.depend_data["FactorData.Basic_factor.close_badj"]
        volume = single_database.depend_data["FactorData.Basic_factor.volume"]
        close_minute = single_database.depend_data["FactorData.Basic_factor.close_adj_minute"]
        volume_minute = single_database.depend_data["FactorData.Basic_factor.volume_minute"]

        fmt = '%Y%m%d'
        date_list = np.unique(close_minute.index.strftime(fmt))

        close_today = close_minute.tail(1)
        volume_today = volume_minute.sum().to_frame().T
        volume_today = pd.DataFrame(volume_today.values * 240 / len(volume_minute), index=volume_today.index,
                                    columns=volume_today.columns)
        close_today.index = date_list
        volume_today.index = date_list

        close = close.append(close_today)
        volume = volume.append(volume_today)

        close_ret = pd.DataFrame(close.values / close.shift(1).values,
                                 index=close.index, columns=close.columns)
        volume_ret = pd.DataFrame(volume.values / volume.shift(1).values,
                                  index=volume, columns=volume.columns)

        close_ret_temporal_rank = close_ret.rank(axis=0)
        volume_ret_temporal_rank = volume_ret.rank(axis=0)

        close_ret_temporal_rank = pd.DataFrame(close_ret_temporal_rank.values,
                                               index=close_ret_temporal_rank.index,
                                               columns=close_ret_temporal_rank.columns)
        volume_ret_temporal_rank = pd.DataFrame(volume_ret_temporal_rank.values,
                                                index=volume_ret_temporal_rank.index,
                                                columns=volume_ret_temporal_rank.columns)

        ans = - array_coef(close_ret_temporal_rank, volume_ret_temporal_rank)

        return ans
