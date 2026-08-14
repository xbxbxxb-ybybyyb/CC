# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import time

class HF_VmL2HmVDiffStdRatio(BaseFactor):
    """
    * 因子名：HF_VmL2HmVDiffStdRatio_13h
    * 因子功能描述：T日最低价到成交均价距离与成交均价到最高价距离各自变化量的波动率之比，值越大，说明在支撑位博弈越激烈，未来越可能上涨
    * 因子参数：MinuteHigh,MinuteLow,MinuteVolume,MinuteTurnover
    * 作者：游加平
    * 因子创建日期： 2019.10.23
    """
    factor_type = "FIX"
    # fix_times = ["1300"]
    # depend_factors = ["SampleFactor"]
    depend_data = ["FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.low_minute", 
    "FactorData.Basic_factor.amt_minute","FactorData.Basic_factor.volume_minute"]
    lag = 0
    reform_window = 0

    # def definition(self,MinuteHigh,MinuteLow,MinuteVolume,MinuteTurnover):
    #     factor = self.minute_help(self.minute,'MinuteValidHelp',MinuteHigh,MinuteLow,MinuteVolume,MinuteTurnover)
    #     return factor

    # def minute(self,MinuteHigh,MinuteLow,MinuteVolume,MinuteTurnover):
    #     fmt = '%Y-%m-%d'
    #     date_list = sorted(np.unique(MinuteVolume.index.strftime(fmt)))
    #     compute_date = date_list[-1]

    #     high = MinuteHigh.loc[compute_date].rolling(window=30,min_periods=1).max()
    #     low = MinuteLow.loc[compute_date].rolling(window=30,min_periods=1).min()
    #     volume = MinuteVolume.loc[compute_date].rolling(window=30,min_periods=1).sum()
    #     amt = MinuteTurnover.loc[compute_date].rolling(window=30,min_periods=1).sum()
    #     volume = volume.replace(0.,np.nan)
    #     vwap = amt.cumsum() / volume.cumsum()
    #     ratio = (vwap - low).diff().std() / (high - vwap).diff().std()
    #     return ratio

    def calc_single(self, database):
        MinuteLow = database.depend_data["FactorData.Basic_factor.low_minute"]
        MinuteTurnover = database.depend_data["FactorData.Basic_factor.amt_minute"]
        MinuteVolume = database.depend_data["FactorData.Basic_factor.volume_minute"]
        MinuteHigh = database.depend_data["FactorData.Basic_factor.high_minute"]
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])

        fmt = '%Y-%m-%d'
        date_list = sorted(np.unique(MinuteVolume.index.strftime(fmt)))
        compute_date = date_list[-1]
        
        high = MinuteHigh.loc[compute_date].rolling(window=10,min_periods=1).max()
        low = MinuteLow.loc[compute_date].rolling(window=10,min_periods=1).min()
        volume = MinuteVolume.loc[compute_date].rolling(window=10,min_periods=1).sum()
        amt = MinuteTurnover.loc[compute_date].rolling(window=10,min_periods=1).sum()

        volume = volume.replace(0.,np.nan)
        vwap = amt.cumsum() / volume.cumsum()
        ratio = (vwap - low).diff().std() / (high - vwap).diff().std()
        return ratio

        
