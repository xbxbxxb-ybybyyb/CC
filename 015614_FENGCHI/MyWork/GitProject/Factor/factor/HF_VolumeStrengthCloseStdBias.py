# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform

class HF_VolumeStrengthCloseStdBias(BaseFactor):
    """
    *因子名 : HF_VolumeStrengthCloseStdBias_13h
    *因子功能描述 : 成交量与收盘价波动率的相关性，值越大，表示炒作越多，收益越低
    *因子参数 : MinuteClose-分钟收盘价，MinuteVolume-分钟成交量
    *作者 : hezq
    *因子创建日期 : 2019.7.30

    """
    factor_type = "FIX"
    # fix_times = ["1300"]
    # depend_factors = ["SampleFactor"]
    depend_data = ["FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.close_minute"]
    lag = 0
    reform_window = 30

#     def definition(self,MinuteClose,MinuteVolume):
#         df = self.minute_help(self.minute, 'HF_VolumeStrengthCloseStdBias_13hHelp',MinuteClose,MinuteVolume)
#         df[np.isinf(df)] = np.nan
# #         df = ((df-df.rolling(window=rd,min_periods=1).mean())/df.rolling(window=rd,min_periods=1).std())
#         df = df-df.shift(30).fillna(0)
#         return -df
#     def minute(self,MinuteClose,MinuteVolume): 
#         fmt = '%Y-%m-%d'
#         date_list = np.unique(MinuteClose.index.strftime(fmt))[0]
#         # print(date_list)
#         volume_today = MinuteVolume.sort_index(ascending=True)
#         close = MinuteClose.sort_index(ascending=True)
        
#         close_std = close.rolling(window=5,min_periods=1).std()
#         res = close_std.corrwith(volume_today)
#         return res
    def calc_single(self, database):
        MinuteClose = database.depend_data["FactorData.Basic_factor.close_minute"]
        MinuteVolume = database.depend_data["FactorData.Basic_factor.volume_minute"]
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])

        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))[0]
        # print(date_list)
        volume_today = MinuteVolume.sort_index(ascending=True)
        close = MinuteClose.sort_index(ascending=True)
        
        close_std = close.rolling(window=5,min_periods=1).std()
        # res = close_std.corrwith(volume_today)
        res = Util.array_coef(close_std, volume_today)
        return res

    def reform(self, df):
        df[np.isinf(df)] = np.nan
        df = df-df.shift(30).fillna(0)
        return -df