# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
    
class HF_VolumeStrengthDeg1(BaseFactor):
    """
    *因子名 : HF_VolumeStrengthDeg1_13h
    *因子功能描述 : 成交量相对收盘价的回归系数，值越大，超买，收益越低
    *因子参数 : MinuteClose-分钟收盘价，MinuteVolume-分钟成交量
    *作者 : hezq
    *因子创建日期 : 2019.7.30

    """
    factor_type = "FIX"
    # fix_times = ["1300"]
    # depend_factors = ["SampleFactor"]
    depend_data = ["FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.close_minute"]
    lag = 0
    reform_window = 60

    # def definition(self,MinuteClose,MinuteVolume):
    #     rd=60
    #     df = self.minute_help(self.minute, 'HF_VolumeStrengthDeg1_13hHelp',MinuteClose,MinuteVolume)
    #     df[np.isinf(df)] = np.nan
    #     df = ((df-df.rolling(window=rd,min_periods=1).mean())/df.rolling(window=rd,min_periods=1).std())
    #     return -df
    # def minute(self,MinuteClose,MinuteVolume): 
    #     fmt = '%Y-%m-%d'
    #     date_list = np.unique(MinuteClose.index.strftime(fmt))[0]
    #     # print(date_list)
    #     volume_today = MinuteVolume.sort_index(ascending=True)
    #     close = MinuteClose.sort_index(ascending=True)
    #     res = close.corrwith(volume_today)*close.std(axis=0)/volume_today.std(axis=0)
    #     return res

    def calc_single(self, database):
        MinuteClose = database.depend_data["FactorData.Basic_factor.close_minute"]
        MinuteVolume = database.depend_data["FactorData.Basic_factor.volume_minute"]
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])

        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))[0]
        # print(date_list)
        volume_today = MinuteVolume.sort_index(ascending=True)
        close = MinuteClose.sort_index(ascending=True)
        # res = close.corrwith(volume_today)*close.std(axis=0)/volume_today.std(axis=0)
        res = Util.array_coef(volume_today, close) *close.std(axis=0)/volume_today.std(axis=0)
        return res

    def reform(self, df):
        rd=60
        df[np.isinf(df)] = np.nan
        df = ((df-df.rolling(window=rd,min_periods=1).mean())/df.rolling(window=rd,min_periods=1).std())
        return -df


