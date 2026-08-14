# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import time

class HF_VolumeAmtSkewRatio(BaseFactor):
    """
    * 因子名：HF_VolumeAmtSkewRatio_13h
    * 因子功能描述：相对全市场成交量的加权偏度与成交额的加权偏度对比，说明成交额分布更加左偏，代表在相对低价位上成交量较大，未来可能上涨
    * 因子参数：MinuteVolume,MinuteTurnover
    * 作者：游加平
    * 因子创建日期： 2019.10.25
    """
    factor_type = "FIX"
    # fix_times = ["1300"]
    # depend_factors = ["SampleFactor"]
    depend_data = ["FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.low_minute", 
    "FactorData.Basic_factor.amt_minute","FactorData.Basic_factor.close_minute"]
    lag = 0
    minute_lag=0
    
    # def definition(self,MinuteVolume,MinuteTurnover):
    #     factor = self.minute_help(self.minute,'MinuteValidHelp',MinuteVolume,MinuteTurnover)
    #     return factor

    # def minute(self,MinuteVolume,MinuteTurnover):
    #     fmt = '%Y-%m-%d'
    #     date_list = sorted(np.unique(MinuteVolume.index.strftime(fmt)))
    #     compute_date = date_list[-1]

    #     amt = MinuteTurnover.loc[compute_date].resample('5min').sum()
    #     volume = MinuteVolume.loc[compute_date].resample('5min').sum()
    #     amt = amt.div(amt.sum(axis=1),axis=0)
    #     volume = amt.div(volume.sum(axis=1),axis=0)
    #     skew = self.compute_skew(volume) / self.compute_skew(amt)
    #     return skew

    def compute_skew(self,df):
        weight = np.arange(1,df.shape[0]+1)
        weight = weight / weight.sum()
        mean = df.mul(weight,axis=0).sum()
        # var = ((df - mean)**2).mul(weight,axis=0).sum()
        var = pd.DataFrame(np.multiply((np.subtract(df.values,mean.values)**2).T, weight).T,
         index=df.index, columns=df.columns).sum()
        # three = (np.subtract(df,mean)**3).mul(weight,axis=0).sum()
        three = pd.DataFrame(np.multiply((np.subtract(df.values,mean.values)**3).T, weight).T,
         index=df.index, columns=df.columns).sum()
        std = np.sqrt(var)
        skew = - three / std**3

        return skew

    def calc_single(self, database):
        MinuteTurnover = database.depend_data["FactorData.Basic_factor.amt_minute"]
        MinuteVolume = database.depend_data["FactorData.Basic_factor.volume_minute"]
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])

        fmt = '%Y-%m-%d'
        date_list = sorted(np.unique(MinuteVolume.index.strftime(fmt)))
        compute_date = date_list[-1]
        
        amt = MinuteTurnover.loc[compute_date].resample('5min').sum()
        volume = MinuteVolume.loc[compute_date].resample('5min').sum()
        # below not time consuming
        amt = amt.div(amt.sum(axis=1),axis=0)
        volume = amt.div(volume.sum(axis=1),axis=0)
        skew = self.compute_skew(volume) / self.compute_skew(amt)
        
        return skew
