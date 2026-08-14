# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np
import copy
from collections import Counter
class CorrVolumePriceRankSharpe(BaseFactor):

    """
    *因子名：CorrVolumePriceRankSharpe_13h
    *因子功能描述：当日截至13:00，量价秩相关性,取前5日夏普。
    相关性越低，说明价格在低位时成交量大，在高位时成交量小，后市有上涨趋势。
    *因子参数：[MinuteClose]: 分钟收盘价
               [MinuteVolume]: 分钟成交量

    *作者：周璇
    *因子创建日期：2019.7.29
    *函数修改日期：尚未修改
    *修改人：尚未修改
    *修改原因：尚未修改
    """
    factor_type = 'FIX'
    s_close_min = 'FactorData.Basic_factor.close_minute'
    s_volume_min = 'FactorData.Basic_factor.volume_minute'
    depend_data = [s_close_min, s_volume_min]
    n = 5
    minute_lag = n - 1

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        close_min = database.depend_data[self.s_close_min]
        volume_min = database.depend_data[self.s_volume_min]
        CorrVolumePriceSharpe = self.minute(close_min, volume_min)
        return -CorrVolumePriceSharpe


    def minute(self, MinuteClose,MinuteVolume):
        fmt = '%Y-%m-%d'
        datelist = sorted(np.unique(MinuteClose.index.strftime(fmt)))
        CorrVolumePrice = pd.DataFrame(index=[pd.Timestamp(date) for date in datelist],columns=MinuteClose.columns)
        for date in datelist:
            close_min = MinuteClose.loc[date]
            volume_min = MinuteVolume.loc[date]
            volume_min=volume_min.convert_objects(convert_numeric=True)
            CorrVolumePrice.loc[date] = Util.array_coef(volume_min.rank(axis=0), close_min.rank(axis=0))
        return CorrVolumePrice.mean(axis=0)/CorrVolumePrice.std(axis=0)
        