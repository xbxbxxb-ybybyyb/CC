# -*- coding: utf-8 -*-
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
class Min30CEMVbias(BaseFactor):
    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.high_minute","FactorData.Basic_factor.open_minute",
    "FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.low_minute","FactorData.Basic_factor.amt_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    reform_window=40
    fix_times=["1500"]

    def calc_single(self, database): 
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        MinuteHigh = database.depend_data['FactorData.Basic_factor.high_minute']
        MinuteLow = database.depend_data['FactorData.Basic_factor.low_minute']
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteOpen = database.depend_data['FactorData.Basic_factor.open_minute']
        MinuteTurnover = database.depend_data['FactorData.Basic_factor.amt_minute']
        
        dailyf = self.minute_help( MinuteClose, MinuteOpen, MinuteHigh, MinuteLow, MinuteTurnover, MinuteVolume)
        # dailyf1 = (dailyf.astype(float) - dailyf.rolling(window=20, min_periods=5).mean()) / (dailyf.rolling(window=20, min_periods=5).std())
        # alpha = -dailyf1.iloc[-20:,:].mean()
        # alpha[dailyf1.iloc[-20:,:].notnull().sum()<10]=np.nan
        return dailyf

    def divide_df_series(self,df,seris):
        return pd.DataFrame(df.values/seris.values,index=df.index,columns=df.columns)
    
    def minute_help(self, MinuteClose, MinuteOpen, MinuteHigh, MinuteLow, MinuteTurnover, MinuteVolume): 
        fmt = '%Y-%m-%d' 
        date_list = np.unique(MinuteOpen.index.strftime(fmt)) 
        # df_ratio = pd.DataFrame(index=[pd.Timestamp(date) for date in date_list], columns=MinuteOpen.columns) 
        for date in date_list:
            close = MinuteClose.loc[date] 
            high = MinuteHigh.loc[date]
            low = MinuteLow.loc[date]
            volume = MinuteVolume.loc[date]
            high =  self.divide_df_series(high,high.mean())
            low = self.divide_df_series(low,low.mean())
            close = self.divide_df_series(close,close.mean())
            volume = self.divide_df_series(volume,volume.mean())
            price_range = high - low
            mid_price = (high + low) 
            mid_price = pd.DataFrame(mid_price.values/2,index=mid_price.index,columns=mid_price.columns)
            df_ratio = (volume.iloc[-30:,] * price_range.iloc[-30:,] * (mid_price.iloc[-30:,] - mid_price.iloc[-30:,].shift(1))).mean()
        return df_ratio
    def reform(self,temp_result):
        dailyf = temp_result
        dailyf1 = (dailyf.astype(float) - dailyf.rolling(window=20, min_periods=5).mean()) / (dailyf.rolling(window=20, min_periods=5).std())
        alpha = dailyf1.rolling(window=20, min_periods=10).mean()
        return -alpha

