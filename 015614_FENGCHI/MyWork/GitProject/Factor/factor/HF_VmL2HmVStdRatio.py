# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import time

class HF_VmL2HmVStdRatio(BaseFactor):
    """
    * 因子名：HF_VmL2HmVStdRatio_13h
    * 因子功能描述：Vwap减去Low的波动率与High减去Vwap波动率之比
    * 因子参数：MinuteHigh,MinuteLow,MinuteVolume,MinuteTurnover
    * 作者：游加平
    * 因子创建日期： 2019.9.20
    """
    factor_type = "FIX"
    # fix_times = ["1300"]
    # depend_factors = ["SampleFactor"]
    depend_data = ["FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.low_minute", 
    "FactorData.Basic_factor.amt_minute","FactorData.Basic_factor.volume_minute"]
    lag = 0
    reform_window = 20

    # def definition(self,MinuteHigh,MinuteLow,MinuteVolume,MinuteTurnover):
    #     factor = self.minute_help(self.minute,'MinuteValidHelp',MinuteHigh,MinuteLow,MinuteVolume,MinuteTurnover)
    #     factor = self.zscore(factor,window=20)
    #     return factor

    # def minute(self,MinuteHigh,MinuteLow,MinuteVolume,MinuteTurnover):
    #     fmt = '%Y-%m-%d'
    #     date_list = sorted(np.unique(MinuteVolume.index.strftime(fmt)))
    #     compute_date = date_list[-1]
        
    #     high = MinuteHigh.loc[compute_date].rolling(window=5,min_periods=1).max()
    #     low = MinuteLow.loc[compute_date].rolling(window=5,min_periods=1).min()
    #     volume = MinuteVolume.loc[compute_date].rolling(window=5,min_periods=1).sum()
    #     amt = MinuteTurnover.loc[compute_date].rolling(window=5,min_periods=1).sum()

    #     volume[volume==0.] = np.nan
    #     vwap = amt.cumsum() / volume.cumsum()
    #     rolling_high = high.rolling(window=5,min_periods=1).mean()
    #     rolling_low = low.rolling(window=5,min_periods=1).mean()
    #     ratio = (vwap - rolling_low).std() / (rolling_high - vwap).std()
    #     return ratio

    def rolling_mean(self,factor,window):
        return factor.rolling(window=window,min_periods=1).mean()
    
    def rolling_std(self,factor,window):
        return factor.rolling(window=window,min_periods=1).std()
    
    def zscore(self,factor,window=5):
        return (factor-self.rolling_mean(factor,window=window)) / self.rolling_std(factor,window=window)

    def calc_single(self, database):
        MinuteLow = database.depend_data["FactorData.Basic_factor.low_minute"]
        MinuteTurnover = database.depend_data["FactorData.Basic_factor.amt_minute"]
        MinuteVolume = database.depend_data["FactorData.Basic_factor.volume_minute"]
        MinuteHigh = database.depend_data["FactorData.Basic_factor.high_minute"]
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])

        fmt = '%Y-%m-%d'
        date_list = sorted(np.unique(MinuteVolume.index.strftime(fmt)))
        compute_date = date_list[-1]
        
        high = MinuteHigh.loc[compute_date].rolling(window=5,min_periods=1).max()
        low = MinuteLow.loc[compute_date].rolling(window=5,min_periods=1).min()
        volume = MinuteVolume.loc[compute_date].rolling(window=5,min_periods=1).sum()
        amt = MinuteTurnover.loc[compute_date].rolling(window=5,min_periods=1).sum()

        # volume[volume==0.] = np.nan
        volume[pd.DataFrame(volume.values==0, index=volume.index, columns=volume.columns)] = np.nan
        vwap = amt.cumsum() / volume.cumsum()
        rolling_high = high.rolling(window=5,min_periods=1).mean()
        rolling_low = low.rolling(window=5,min_periods=1).mean()
        ratio = (vwap - rolling_low).std() / (rolling_high - vwap).std()
        return ratio

    def reform(self, factor):
        factor = self.zscore(factor,window=20)
        return factor