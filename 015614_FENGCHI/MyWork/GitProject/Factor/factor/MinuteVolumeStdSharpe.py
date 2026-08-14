# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform


class MinuteVolumeStdSharpe(BaseFactor):

    """
    * 因子名：MinuteVolumeStdSharpe
    * 因子功能描述：计算日内交易量标准差的稳定性。
    * 因子参数：MinuteVolume
    * 作者：姚逸凡
    * 因子创建日期： 2019.1.15
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
    """

    factor_type = "DAY"
    # fix_times = ["1500"]
    # depend_factors = ["SampleFactor"]
    depend_data = ["FactorData.Basic_factor.volume_minute"]
    lag = 0
    reform_window = 10

    # def definition(self, MinuteVolume):

    #     result = self.minute_help(self.minute, 'MinuteVolumeStdSharpe', MinuteVolume)
    #     result = self.Mean(result, 10) / self.Stdev(result, 10)
    #     return result

    def Mean(self, DF, lag):

        meanDF = DF.rolling(window=lag, min_periods=1).mean()
        return meanDF

    def Stdev(self,DF, lag):

        stdDF = DF.rolling(window=lag, min_periods=1).std()
        return stdDF

    # def minute(self, MinuteVolume):

    #     fmt = '%Y-%m-%d'
    #     date_list = np.unique(MinuteVolume.index.strftime(fmt))
    #     result_df = pd.DataFrame(np.nan, index=[pd.Timestamp(date) for date in date_list], columns=MinuteVolume.columns)

    #     for date in date_list:
    #         volume_df = MinuteVolume.loc[date]
    #         volume_df = volume_df.resample('5T').sum()

    #         std = volume_df.std()
    #         if len(std.dropna()) != 0:
    #             result_df.loc[date] = std
    #         else:
    #             result_df.loc[date] = 0.0

    #     return result_df

    def calc_single(self, database):
        MinuteVolume = database.depend_data["FactorData.Basic_factor.volume_minute"]
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])

        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteVolume.index.strftime(fmt))
        result_df = pd.DataFrame(np.nan, index=[pd.Timestamp(date) for date in date_list], columns=MinuteVolume.columns)

        for date in date_list:
            volume_df = MinuteVolume.loc[date]
            volume_df = volume_df.resample('5T').sum()

            std = volume_df.std()
            if len(std.dropna()) != 0:
                result_df.loc[date] = std
            else:
                result_df.loc[date] = 0.0
        return result_df.iloc[-1,:]

    def reform(self, result):
        result = self.Mean(result, 10) / self.Stdev(result, 10)
        return result
