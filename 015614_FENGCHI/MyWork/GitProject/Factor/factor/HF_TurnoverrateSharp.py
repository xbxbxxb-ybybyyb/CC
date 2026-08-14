# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform

class HF_TurnoverrateSharp(BaseFactor):
    """
    *因子名 : HF_TurnoverrateSharp_13h
    *因子功能描述 : 分钟换手率（成交量除以总股本）来表示分钟的非流动性，用波动率调整的平均值捕捉非流动性的异常
    *因子参数 : MinuteClose-分钟收盘价，MinuteVolume-分组成交量
    *作者 : hezq
    *因子创建日期 : 2019.6.21

    """
    factor_type = "FIX"
    # fix_times = ["1300"]
    # depend_factors = ["SampleFactor"]
    depend_data = ["FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.float_a_shares"]
    lag = 1
    minute_lag = 1
    reform_window = 10

    # def definition(self,MinuteVolume,float_a_shares):
    #     df = self.minute_help(self.minute, 'HF_TurnoverrateSharp_13hHelp',MinuteVolume,float_a_shares)
    #     df = df.rolling(window=10,min_periods=1).mean()/df.rolling(window=10,min_periods=1).std()
    #     df[np.isinf(df)] = np.nan
    #     return df
    # def minute(self,MinuteVolume,float_a_shares): 

    #     fmt = '%Y-%m-%d'
    #     date_list = sorted(np.unique(MinuteVolume.index.strftime(fmt)))
    #     # print(date_list[-1])
    #     volume_today = MinuteVolume.loc[date_list[-1]].sort_index(ascending=True)
    #     total_shares = float_a_shares.loc[date_list[0]]

    #     total_shares[total_shares==0]= 0
    #     turnover = volume_today.div(total_shares,axis=1)
    #     res = turnover.mean(axis=0)
    #     return res

    def calc_single(self, database):
        MinuteVolume = database.depend_data["FactorData.Basic_factor.volume_minute"]
        float_a_shares = database.depend_data["FactorData.Basic_factor.float_a_shares"]
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])

        fmt = '%Y%m%d'
        date_list = sorted(np.unique(MinuteVolume.index.strftime(fmt)))
        # print(date_list[-1])
        volume_today = MinuteVolume.loc[date_list[-1]].sort_index(ascending=True)
        total_shares = float_a_shares.loc[date_list[0]].reindex(volume_today.columns)

        total_shares[total_shares==0]= 0
        # turnover = volume_today.div(total_shares,axis=1)
        turnover = pd.DataFrame(np.divide(volume_today.values, total_shares.values), 
            index=volume_today.index, columns=volume_today.columns)
        res = turnover.mean(axis=0)
        return res
    def reform(self, df):
        df = df.rolling(window=10,min_periods=1).mean()/df.rolling(window=10,min_periods=1).std()
        df[np.isinf(df)] = np.nan
        return df