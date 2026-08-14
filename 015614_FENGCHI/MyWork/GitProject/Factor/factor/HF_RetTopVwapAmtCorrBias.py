# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import time

class HF_RetTopVwapAmtCorrBias(BaseFactor):

    """
    * 因子名：HF_RetTopVwapAmtCorrBias_13h
    * 因子功能描述：前20%收益率时刻Vwap与成交额的相关系数，与最小值偏度
    * 因子参数：MinuteClose,MinuteVolume,MinuteTurnover
    * 作者：游加平
    * 因子创建日期： 2019.8.26
    """
    factor_type = "FIX"
    # fix_times = ["1300"]
    # depend_factors = ["SampleFactor"]
    depend_data = ["FactorData.Basic_factor.volume_minute",
    "FactorData.Basic_factor.amt_minute","FactorData.Basic_factor.close_minute"]
    lag = 0
    reform_window = 10

    # def definition(self,MinuteClose,MinuteVolume,MinuteTurnover):
    #     factor = self.minute_help(self.minute,'MinuteValidHelp',MinuteClose,MinuteVolume,MinuteTurnover)
    #     factor = factor / factor.rolling(window=10,min_periods=1).min()
    #     factor.fillna(0.,inplace=True)
    #     return factor

    # def minute(self,MinuteClose,MinuteVolume,MinuteTurnover):
    #     fmt = '%Y-%m-%d'
    #     date_list = sorted(np.unique(MinuteVolume.index.strftime(fmt)))
    #     compute_date = date_list[-1]
        
    #     ret = MinuteClose.loc[compute_date].pct_change()
    #     ret_quantile = ret.quantile(0.8)        
    #     amt = MinuteTurnover.loc[compute_date].rolling(window=5,min_periods=1).mean()
    #     volume = MinuteVolume.loc[compute_date].rolling(window=5,min_periods=1).mean()
    #     amt_pos = amt[ret>ret_quantile]
    #     volume_pos = volume[ret>ret_quantile]
    #     vwap_pos = amt_pos / volume_pos
    #     corr = vwap_pos.corrwith(amt_pos)      
    #     return corr
    def calc_single(self, database):
        MinuteTurnover = database.depend_data["FactorData.Basic_factor.amt_minute"]
        MinuteVolume = database.depend_data["FactorData.Basic_factor.volume_minute"]
        MinuteClose = database.depend_data["FactorData.Basic_factor.close_minute"]
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        fmt = '%Y%m%d'
        date_list = sorted(np.unique(MinuteVolume.index.strftime(fmt)))
        compute_date = date_list[-1]
        t1 = time.time()
        # ret = MinuteClose.loc[compute_date].pct_change()
        ret = (MinuteClose.loc[compute_date] - MinuteClose.loc[compute_date].shift(1))/MinuteClose.loc[compute_date].shift(1)
        ret_quantile = ret.quantile(0.8)        
        amt = MinuteTurnover.loc[compute_date].rolling(window=5,min_periods=1).mean()
        volume = MinuteVolume.loc[compute_date].rolling(window=5,min_periods=1).mean()
        # amt_pos = amt[ret>ret_quantile]
        amt_pos = amt[pd.DataFrame(np.subtract(ret.values,ret_quantile.values)>0,
            index=ret.index, columns=ret.columns)]
        # volume_pos = volume[ret>ret_quantile]
        volume_pos = volume[pd.DataFrame(np.subtract(ret.values,ret_quantile.values)>0,
            index=ret.index, columns=ret.columns)]
        vwap_pos = amt_pos / volume_pos
        # corr = vwap_pos.corrwith(amt_pos)      
        corr = Util.array_coef(vwap_pos, amt_pos)
        return corr
    def reform(self, factor):
        factor = factor / factor.rolling(window=10,min_periods=1).min()
        # factor.fillna(0.,inplace=True)
        return factor