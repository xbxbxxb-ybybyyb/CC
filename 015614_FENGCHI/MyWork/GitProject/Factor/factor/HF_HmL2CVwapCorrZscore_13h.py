# coding: utf-8

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform


class HF_HmL2CVwapCorrZscore_13h(BaseFactor):

    """
    * 因子名：HF_HmL2CVwapCorr_13h
    * 因子功能描述：(High-Low)/Close与Vwap的秩相关系数，取负号
    * 因子参数：MinuteHigh,MinuteLow,MinuteClose,MinuteVolume,MinuteTurnover
    * 作者：游加平
    * 因子创建日期： 2019.8.2
    """
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.close_minute",\
    "FactorData.Basic_factor.low_minute", "FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.amt_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
    reform_window = 5


    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        MinuteHigh = database.depend_data['FactorData.Basic_factor.high_minute']  
        MinuteLow = database.depend_data['FactorData.Basic_factor.low_minute']  
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']  
        MinuteTurnover = database.depend_data['FactorData.Basic_factor.amt_minute']  

        fmt = '%Y-%m-%d'
        date_list = sorted(np.unique(MinuteHigh.index.strftime(fmt)))
        compute_date = date_list[-1]

        high = MinuteHigh.loc[compute_date]
        low = MinuteLow.loc[compute_date]
        close = MinuteClose.loc[compute_date]
        amt = MinuteTurnover.loc[compute_date]
        volume = MinuteVolume.loc[compute_date] 
           
        df = ( (high - low ) / close ).rank(axis=1)
        vwap_rank = (amt / volume).rank(axis=1)
        res_corr = Util.array_coef(df,vwap_rank)
        return -res_corr

    def rolling_mean(self,factor,window):
        res = factor.rolling(window=window,min_periods=1).mean()
        return res

    def rolling_std(self,factor,window):
        res = factor.rolling(window=window,min_periods=1).std()
        return res

    def zscore(self,factor):
        window = self.reform_window
        res = (factor-self.rolling_mean(factor,window))/self.rolling_std(factor,window)
        return res

    def reform(self, df):
        df = self.zscore(df)
        return df        


    

