# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform

class HF_PriceDiffRatio(BaseFactor):
    """
    * 因子名：HF_PriceDiffRatio_13h
    * 因子功能描述：T日阻力位减去Vwap均值与Vwap均值减去支撑位之比，值越大，说明当前价格处于相对低位，未来越容易上涨
    * 因子参数：MinuteHigh,MinuteLow,MinuteVolume,MinuteTurnover
    * 作者：游加平
    * 因子创建日期： 2019.9.30
    """
    factor_type = "FIX"
    # fix_times = ["1300"]
    # depend_factors = ["SampleFactor"]
    depend_data = ["FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.low_minute", 
    "FactorData.Basic_factor.amt_minute","FactorData.Basic_factor.high_minute"]
    lag = 0
    reform_window = 2

    # def definition(self,MinuteHigh,MinuteLow,MinuteVolume,MinuteTurnover):
    #     factor = self.minute_help(self.minute,'MinuteValidHelp',MinuteHigh,MinuteLow,MinuteVolume,MinuteTurnover)
    #     factor = self.rolling_min(factor,window=2)
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
    #     ratio = (rolling_high - rolling_mean).mean() / (rolling_mean - rolling_low).mean()  
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
        ratio = (rolling_high - rolling_mean) /  (rolling_mean - rolling_low)
        return -ratio.iloc[-1,:]

    def reform(self, factor):
        factor = self.rolling_min(factor,window=2)
        return factor

