# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform

class HF_VolumeStdStrengthCloseChangePct(BaseFactor):
    """
    *因子名 :  HF_VolumeStdStrengthCloseChangePct_13h
    *因子功能描述 : 成交量波动率与收盘价的相关性,取相对偏离值;值越大，表示放量超买，收益越低
    *因子参数 : MinuteClose-分钟收盘价，MinuteVolume-分钟成交量
    *作者 : hezq
    *因子创建日期 : 2019.08.02
    """
    factor_type = "FIX"
    # fix_times = ["1300"]
    # depend_factors = ["SampleFactor"]
    depend_data = ["FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.close_minute"]
    lag = 0
    reform_window = 21
    # def definition(self,MinuteClose,MinuteVolume):
    #     rd=20
    #     df = self.minute_help(self.minute, 'HF_VolumeStdStrengthCloseChangePct_13hHelp',MinuteClose,MinuteVolume)
    #     df[np.isinf(df)] = np.nan
    #     df = (df-df.shift(rd))/abs(df.shift(rd))
    #     df.loc[df.notnull().sum(axis=1)==0] = 0
    #     return -df
    # def minute(self,MinuteClose,MinuteVolume): 
    #     fmt = '%Y-%m-%d'
    #     date_list = np.unique(MinuteClose.index.strftime(fmt))[0]
    #     # print(date_list)
    #     volume_today = MinuteVolume.sort_index(ascending=True)
    #     close = MinuteClose.sort_index(ascending=True)
        
    #     volume_std = volume_today.rolling(window=5,min_periods=1).std()
    #     res = close.corrwith(volume_std)
    #     return res

    def calc_single(self, database):
        MinuteVolume = database.depend_data["FactorData.Basic_factor.volume_minute"]
        MinuteClose = database.depend_data["FactorData.Basic_factor.close_minute"]
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])

        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))[0]
        # print(date_list)
        volume_today = MinuteVolume.sort_index(ascending=True)
        close = MinuteClose.sort_index(ascending=True)

        volume_std = volume_today.rolling(window=5,min_periods=1).std()
        # res = close.corrwith(volume_std)
        res = Util.array_coef(close, volume_std)
        return res

    def reform(self, df):
        rd=20
        df[np.isinf(df)] = np.nan
        df = (df-df.shift(rd))/abs(df.shift(rd))
        df.loc[df.notnull().sum(axis=1)==0] = 0
        return -df