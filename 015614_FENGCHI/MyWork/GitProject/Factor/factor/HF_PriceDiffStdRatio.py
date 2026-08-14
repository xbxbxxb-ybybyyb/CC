# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform

class HF_PriceDiffStdRatio(BaseFactor):
    """
    * 因子名：HF_PriceDiffStdRatio_13h
    * 因子功能描述：T日阻力位减去Vwap均值和Vwap均值减去支撑位两者的波动率之比
    * 因子参数：MinuteHigh,MinuteLow,MinuteVolume,MinuteTurnover
    * 作者：游加平
    * 因子创建日期： 2019.10.08
    """
    factor_type = "FIX"
    # fix_times = ["1300"]
    # depend_factors = ["SampleFactor"]
    depend_data = ["FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.low_minute", 
    "FactorData.Basic_factor.amt_minute","FactorData.Basic_factor.high_minute"]
    lag = 0

    # def definition(self,MinuteHigh,MinuteLow,MinuteVolume,MinuteTurnover):
    #     factor = self.minute_help(self.minute,'MinuteValidHelp',MinuteHigh,MinuteLow,MinuteVolume,MinuteTurnover)
    #     return factor

    # def minute(self,MinuteHigh,MinuteLow,MinuteVolume,MinuteTurnover):
    #     fmt = '%Y-%m-%d'
    #     date_list = sorted(np.unique(MinuteVolume.index.strftime(fmt)))
    #     compute_date = date_list[-1]
        
    #     high = MinuteHigh.loc[compute_date]
    #     low = MinuteLow.loc[compute_date]        
    #     volume = MinuteVolume.loc[compute_date]
    #     amt = MinuteTurnover.loc[compute_date]
    #     vwap = amt / volume
    #     window = vwap.shape[0]
    #     rolling_mean = self.rolling_mean(vwap,window)
    #     rolling_high = self.rolling_max(high,window)
    #     rolling_low = self.rolling_min(low,window)
    #     ratio = (rolling_high - rolling_mean).std() /  (rolling_mean - rolling_low).std()
    #     return -1*ratio

    def rolling_min(self,factor,window):
        return factor.rolling(window=window,min_periods=1).min()

    def rolling_max(self,factor,window):
        return factor.rolling(window=window,min_periods=1).max()
    
    def rolling_mean(self,factor,window):
        return factor.rolling(window=window,min_periods=1).mean()

    def calc_single(self, database):
        MinuteLow = database.depend_data["FactorData.Basic_factor.low_minute"]
        MinuteTurnover = database.depend_data["FactorData.Basic_factor.amt_minute"]
        MinuteVolume = database.depend_data["FactorData.Basic_factor.volume_minute"]
        MinuteHigh = database.depend_data["FactorData.Basic_factor.high_minute"]
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])

        fmt = '%Y%m%d'
        date_list = sorted(np.unique(MinuteVolume.index.strftime(fmt)))
        compute_date = date_list[-1]
        
        high = MinuteHigh.loc[compute_date]
        low = MinuteLow.loc[compute_date]        
        volume = MinuteVolume.loc[compute_date]
        amt = MinuteTurnover.loc[compute_date]
        vwap = amt / volume
        window = vwap.shape[0]
        rolling_mean = self.rolling_mean(vwap,window)
        rolling_high = self.rolling_max(high,window)
        rolling_low = self.rolling_min(low,window)
        ratio = (rolling_high - rolling_mean).std() /  (rolling_mean - rolling_low).std()
        return -ratio
