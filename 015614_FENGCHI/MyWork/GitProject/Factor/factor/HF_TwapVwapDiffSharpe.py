# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform

class HF_TwapVwapDiffSharpe(BaseFactor):
    """
    * 因子名：HF_TwapVwapDiffSharpe_13h
    * 因子功能描述：T日Twap与滚动Vwap之差(衡量股价高于实际成交均价的程度)的夏普率，值越大，说明股价稳步上涨的空间越大
    * 因子参数：MinuteClose, MinuteVolume, MinuteTurnover
    * 作者：游加平
    * 因子创建日期： 2019.10.22
    """
    factor_type = "FIX"
    # fix_times = ["1300"]
    # depend_factors = ["SampleFactor"]
    depend_data = ["FactorData.Basic_factor.volume_minute",
    "FactorData.Basic_factor.amt_minute","FactorData.Basic_factor.close_minute"]
    lag = 0
    reform_window = 5

    # def definition(self,MinuteClose,MinuteVolume,MinuteTurnover):
    #     factor = self.minute_help(self.minute,'MinuteValidHelp',MinuteClose,MinuteVolume,MinuteTurnover)
    #     factor = - factor / self.rolling_min(factor,window=5)
    #     factor[np.isnan(factor).all(axis=1)] = 0.
    #     return factor
    
    # def minute(self,MinuteClose,MinuteVolume,MinuteTurnover):
    #     fmt = '%Y-%m-%d'
    #     date_list = sorted(np.unique(MinuteVolume.index.strftime(fmt)))
    #     compute_date = date_list[-1]
             
    #     close = MinuteClose.loc[compute_date]
    #     volume = MinuteVolume.loc[compute_date]
    #     amt = MinuteTurnover.loc[compute_date]
    #     volume = volume.replace(0.,np.nan)
    #     vwap = amt.cumsum() / volume.cumsum()
    #     twap = close.cumsum().div(np.arange(1,close.shape[0]+1),axis=0)
    #     diff = twap - vwap
    #     sharpe = diff.mean() / diff.std()
    #     return sharpe
 
    def rolling_min(self,factor,window):
        return factor.rolling(window=window,min_periods=1).min()

    def calc_single(self, database):
        MinuteTurnover = database.depend_data["FactorData.Basic_factor.amt_minute"]
        MinuteVolume = database.depend_data["FactorData.Basic_factor.volume_minute"]
        MinuteClose = database.depend_data["FactorData.Basic_factor.close_minute"]
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])

        fmt = '%Y%m%d'
        date_list = sorted(np.unique(MinuteVolume.index.strftime(fmt)))
        compute_date = date_list[-1]
             
        close = MinuteClose.loc[compute_date]
        volume = MinuteVolume.loc[compute_date]
        amt = MinuteTurnover.loc[compute_date]
        volume = volume.replace(0.,np.nan)
        vwap = amt.cumsum() / volume.cumsum()
        twap = close.cumsum().div(np.arange(1,close.shape[0]+1),axis=0)
        diff = twap - vwap
        sharpe = diff.mean() / diff.std()
        return sharpe

    def reform(self, factor):
        factor = - factor / self.rolling_min(factor,window=5)
        # factor[np.isnan(factor).all(axis=1)] = 0.
        return factor
