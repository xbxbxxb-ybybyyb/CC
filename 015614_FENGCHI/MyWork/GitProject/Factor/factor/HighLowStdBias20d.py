# -*- coding: utf-8 -*-
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
class HighLowStdBias20d(BaseFactor):
    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.high_minute","FactorData.Basic_factor.low_minute","FactorData.Basic_factor.close_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    reform_window=20
    minute_lag = 0
    
    # fix_times=["1300"]
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        MinuteLow = database.depend_data['FactorData.Basic_factor.low_minute']
        MinuteHigh = database.depend_data['FactorData.Basic_factor.high_minute']
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        factor = self.minute_help( MinuteHigh, MinuteLow,MinuteClose)
        return factor
    def reform(self,temp_result):
        factor = temp_result
        res = -(factor - factor.rolling(20).mean())/(factor).rolling(20).std()
        return res
    def mul_df_series(self,df,series):
        return pd.DataFrame(df.values*series.values,index=df.index,columns=df.columns)   
    def add_df_series(self,df,series):
        return pd.DataFrame(df.values+series.values,index=df.index,columns=df.columns) 
    
    def minute_help(self, MinuteHigh, MinuteLow,MinuteClose):
        date_list = sorted(np.unique(MinuteClose.index.strftime('%Y-%m-%d')))

        min1re = (MinuteClose.iloc[-1,:]/MinuteClose.iloc[0,:] -1)/(len(MinuteClose)-1)
        tmp = pd.DataFrame(np.repeat(np.array([np.arange(len(MinuteClose))]), len(MinuteClose.columns), axis =0).T ,index = MinuteClose.index, columns = MinuteClose.columns)
        virtual = self.mul_df_series(tmp,min1re*MinuteClose.iloc[0,:])
        virtual = self.add_df_series(virtual,MinuteClose.iloc[0,:])
        highstd = ((MinuteHigh-virtual)/MinuteClose).std()
        lowstd =((MinuteLow-virtual)/MinuteClose).std()
        return  highstd - lowstd

