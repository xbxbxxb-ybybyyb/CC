# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform

class HF_Shortcut2CloseCloseCorrZscore(BaseFactor):

    """
    * 因子名：HF_Shortcut2CloseCloseCorrZscore_13h
    * 因子功能描述：Shortcut/Close与Close的秩相关系数，取负号，取5日Zscore
    * 因子参数：MinuteHigh,MinuteLow,MinuteOpen,MinuteClose
    * 作者：游加平
    * 因子创建日期： 2019.7.31
    """

    factor_type = "FIX"
    # fix_times = ["1300"]
    # depend_factors = ["SampleFactor"]
    depend_data = ["FactorData.Basic_factor.low_minute", "FactorData.Basic_factor.open_minute", 
    "FactorData.Basic_factor.close_minute","FactorData.Basic_factor.high_minute"]
    lag = 0
    reform_window = 5

    # def definition(self,MinuteHigh,MinuteLow,MinuteOpen,MinuteClose):
    #     factor = self.minute_help(self.minute, 'MinuteValidHelp',MinuteHigh,MinuteLow,MinuteOpen,MinuteClose)
    #     factor = self.zscore(factor)
    #     return factor

    # def minute(self,MinuteHigh,MinuteLow,MinuteOpen,MinuteClose):
    #     fmt = '%Y-%m-%d'
    #     date_list = sorted(np.unique(MinuteHigh.index.strftime(fmt)))
    #     compute_date = date_list[-1]

    #     high = MinuteHigh.loc[compute_date]
    #     low = MinuteLow.loc[compute_date]
    #     openp = MinuteOpen.loc[compute_date]
    #     close = MinuteClose.loc[compute_date]
        
    #     shortcut = ((2.*(high - low) - np.abs(openp - close)) / close ).rank(axis=1)
    #     corr =  shortcut.corrwith(close,axis=0)
        
    #     return -1*corr
    
    def rolling_mean(self,factor,window):
        res = factor.rolling(window=window,min_periods=1).mean()
        return res

    def rolling_std(self,factor,window):
        res = factor.rolling(window=window,min_periods=1).std()
        return res

    def zscore(self,factor,window=5):
        res = (factor-self.rolling_mean(factor,window))/self.rolling_std(factor,window)
        return res

    def calc_single(self, database):
        MinuteLow = database.depend_data["FactorData.Basic_factor.low_minute"]
        MinuteOpen = database.depend_data["FactorData.Basic_factor.open_minute"]
        MinuteClose = database.depend_data["FactorData.Basic_factor.close_minute"]
        MinuteHigh = database.depend_data["FactorData.Basic_factor.high_minute"]
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        fmt = '%Y%m%d'
        date_list = sorted(np.unique(MinuteHigh.index.strftime(fmt)))
        compute_date = date_list[-1]

        high = MinuteHigh.loc[compute_date]
        low = MinuteLow.loc[compute_date]
        openp = MinuteOpen.loc[compute_date]
        close = MinuteClose.loc[compute_date]
        
        shortcut = ((pd.DataFrame(2.*(high - low).values,index=high.index, columns=high.columns)
         - np.abs(openp - close)) / close ).rank(axis=1)
        # corr =  shortcut.corrwith(close,axis=0)
        corr = Util.array_coef(shortcut, close)
        return -corr


    def reform(self, factor):
        factor = self.zscore(factor)
        return factor