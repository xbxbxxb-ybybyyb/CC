# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform

class HF_TwapRetWeightSkew(BaseFactor):
    """
    * 因子名：HF_TwapRetWeightSkew_13h
    * 因子功能描述：T日价格对Twap价格收益率的时间加权负偏度，20日最大最小值归一化
    * 因子参数：MinuteClose
    * 作者：游加平
    * 因子创建日期： 2019.10.22
    """
    factor_type = "FIX"
    # fix_times = ["1300"]
    # depend_factors = ["SampleFactor"]
    depend_data = ["FactorData.Basic_factor.close_minute"]
    lag = 0
    reform_window = 20

    # def definition(self,MinuteClose):
    #     factor = self.minute_help(self.minute,'MinuteValidHelp',MinuteClose)
    #     factor = - factor / self.rolling_min(factor,window=20)
    #     factor[np.isnan(factor).all(axis=1)] = 0.
    #     return factor

    # def minute(self,MinuteClose):
    #     fmt = '%Y-%m-%d'
    #     date_list = sorted(np.unique(MinuteClose.index.strftime(fmt)))
    #     compute_date = date_list[-1]
    #     close = MinuteClose.loc[compute_date]
    #     twap = close.cumsum().div(np.arange(1,close.shape[0]+1),axis=0)
    #     ret = close / twap - 1.
        
    #     ret_skew = ret.groupby(pd.Grouper(freq='30min')).skew().dropna(axis=0,how='all')
    #     weight = np.arange(1,ret_skew.shape[0] + 1)
    #     skew = - ret_skew.multiply(weight,axis=0).sum()
    #     return skew

    def rolling_min(self,factor,window):
        return factor.rolling(window=window,min_periods=1).min()

    def calc_single(self, database):
        MinuteClose = database.depend_data["FactorData.Basic_factor.close_minute"]
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])

        fmt = '%Y%m%d'
        date_list = sorted(np.unique(MinuteClose.index.strftime(fmt)))
        compute_date = date_list[-1]
        close = MinuteClose.loc[compute_date]
        twap = close.cumsum().div(np.arange(1,close.shape[0]+1),axis=0)
        # ret = close / twap - 1.
        ret = pd.DataFrame((close/twap).values - 1,index=close.index, columns=close.columns)
        
        ret_skew = ret.groupby(pd.Grouper(freq='30min')).skew().dropna(axis=0,how='all')
        weight = np.arange(1,ret_skew.shape[0] + 1)
        skew = - ret_skew.multiply(weight,axis=0).sum()
        return skew
    def reform(self, factor):
        factor = - factor / self.rolling_min(factor,window=20)
        # factor[np.isnan(factor).all(axis=1)] = 0.
        return factor