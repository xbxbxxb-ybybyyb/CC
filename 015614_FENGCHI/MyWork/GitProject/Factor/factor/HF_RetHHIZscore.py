# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import time


class HF_RetHHIZscore(BaseFactor):

    """
    * 因子名：HF_RetHHIZscore_13h
    * 因子功能描述：分钟正收益率HHI，代表分钟正收益率的聚集程度，聚集度越大，未来越容易下跌
    * 因子参数：MinuteClose
    * 作者：游加平
    * 因子创建日期： 2019.8.12
    """
    factor_type = "FIX"
    # fix_times = ["1300"]
    # depend_factors = ["SampleFactor"]
    depend_data = ["FactorData.Basic_factor.close_minute"]
    lag = 0
    reform_window = 10

    # def definition(self,MinuteClose):
    #     factor = self.minute_help(self.minute,'MinuteValidHelp',MinuteClose)
    #     factor = self.zscore(factor,window=10)
    #     factor.fillna(0.,inplace=True)
    #     return factor

    # def minute(self,MinuteClose):
    #     fmt = '%Y-%m-%d'
    #     date_list = sorted(np.unique(MinuteClose.index.strftime(fmt)))
    #     compute_date = date_list[-1]
        
    #     close = MinuteClose.loc[compute_date]
    #     ret = (close.rolling(window=5,min_periods=1).mean()).pct_change()
    #     rhhipos = self.getHHI(ret[ret>0])
        
    #     return -1*rhhipos
    
    def getHHI(self,df):
        """"""
        # wt = df / df.sum()
        wt = pd.DataFrame(np.divide(df.values, df.sum().values),index=df.index,columns=df.columns)
        hhi = (wt*wt).sum()
        hhi = (hhi - 1./df.shape[0]) / (1. - 1.0/df.shape[0])
        return hhi

    def rolling_mean(self,factor,window):
        return factor.rolling(window=window).mean()
    
    def rolling_std(self,factor,window):
        return factor.rolling(window=window).std()
    
    def zscore(self,factor,window=5):
        return (factor-self.rolling_mean(factor,window=window)) / self.rolling_std(factor,window=window)

    def calc_single(self, database):
        MinuteClose = database.depend_data["FactorData.Basic_factor.close_minute"]
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])

        fmt = '%Y%m%d'
        date_list = sorted(np.unique(MinuteClose.index.strftime(fmt)))
        compute_date = date_list[-1]
        close = MinuteClose.loc[compute_date]
        ret = (close.rolling(window=5,min_periods=1).mean())#.pct_change()
        ret = (ret - ret.shift(1))/ret.shift(1)
        rhhipos = self.getHHI(ret[pd.DataFrame(ret.values>0,index=ret.index,columns=ret.columns)])
        return -rhhipos

    def reform(self, factor):
        factor = self.zscore(factor,window=10)
        # factor.fillna(0.,inplace=True)
        return factor
