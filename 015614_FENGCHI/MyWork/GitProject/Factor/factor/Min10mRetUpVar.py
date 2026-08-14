# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform

class Min10mRetUpVar(BaseFactor):
    """
    * 因子名：Min10mRetUpVar
    * 因子功能描述：日内10分钟k线尾盘上行市场收益率方差与收益率方差之比
    * 因子参数：  MinuteClose
    * 作者：肖倩
    * 因子创建日期： 20190506
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
    """
    factor_type = "DAY"
    # fix_times = ["1500"]
    # depend_factors = ["SampleFactor"]
    depend_data = ["FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.close_minute"]
    lag = 0
    reform_window = 5

    # def definition(self, MinuteClose,MinuteVolume):

    #     result = self.minute_help(self.minute, 'Min10mRetUpVarHelp', MinuteClose,MinuteVolume)
    #     # result = result.rolling(window=5,min_periods=1).mean()
    #     result = result.rolling(window = 5,min_periods=1).apply(lambda x:self.ewm(x))
    #     return -1*result

    # def minute(self, MinuteClose,MinuteVolume):

    #     fmt = '%Y-%m-%d'
    #     date_list = np.unique(MinuteClose.index.strftime(fmt))
    #     result = pd.DataFrame(np.nan, index=[pd.Timestamp(date) for date in date_list], columns=MinuteClose.columns)
    #     for date in date_list:
    #         close_df = MinuteClose.loc[date]
    #         volume_df = MinuteVolume.loc[date]
    #         close_df = close_df.resample('10T').last()
    #         return_df = close_df.pct_change(1)
    #         return_df = return_df.iloc[-15:]
    #         result.loc[date] = return_df[return_df>0].var()/return_df.var()
    #     return result
        
    def ewm(self,x):
        ## series不需要改
        window=len(x)
        seq = [(1-(2.0/(window+1))) ** (window-i) for i in range(1, window + 1)]
        weight = np.array(seq)
        weight_sum = np.sum(weight)
        return np.nansum(x * weight) / weight_sum

    def calc_single(self, database):
        MinuteClose = database.depend_data["FactorData.Basic_factor.close_minute"]
        MinuteVolume = database.depend_data["FactorData.Basic_factor.volume_minute"]
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))
        result = pd.DataFrame(np.nan, index=[pd.Timestamp(date) for date in date_list], columns=MinuteClose.columns)
        for date in date_list:
            close_df = MinuteClose.loc[date]
            volume_df = MinuteVolume.loc[date]
            close_df = close_df.resample('10T').last()
            return_df = close_df.pct_change(1)
            return_df = return_df.iloc[-15:]
            # result.loc[date] = return_df[return_df>0].var()/return_df.var()
            result.loc[date] = return_df[pd.DataFrame(return_df.values>0,
                index=return_df.index, columns=return_df.columns)].var()/return_df.var()
        return result.iloc[-1,:]

    def reform(self, result):
        result = result.rolling(window = 5,min_periods=1).apply(lambda x:self.ewm(x))
        return -result