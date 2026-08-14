# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform

class HF_UpRetAmtSkew(BaseFactor):
    """
    * 因子名：HF_UpRetAmtSkew_13h
    * 因子功能描述：T-1日到T日5分钟K线Vwap上行时刻成交额的负偏度
    * 因子参数：MinuteVolume,MinuteTurnover
    * 作者：游加平
    * 因子创建日期： 2019.10.16
    """
    factor_type = "FIX"
    # fix_times = ["1300"]
    # depend_factors = ["SampleFactor"]
    depend_data = ["FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.amt_minute"]
    lag = 1
    minute_lag = 1

    # def definition(self,MinuteVolume,MinuteTurnover):
    #     factor = self.minute_help(self.minute,'MinuteValidHelp',MinuteVolume,MinuteTurnover)
    #     factor[np.isnan(factor).all(axis=1)] = 0.
    #     return factor

    # def minute(self,MinuteVolume,MinuteTurnover):
    #     fmt = '%Y-%m-%d'
    #     date_list = sorted(np.unique(MinuteVolume.index.strftime(fmt)))
    #     compute_date = date_list[-1]
    #     pre_date = date_list[-2]
        
    #     amt = MinuteTurnover.loc[pre_date:compute_date].resample('5min').sum()
    #     volume = MinuteVolume.loc[pre_date:compute_date].resample('5min').sum()
    #     ret = (amt / volume).pct_change()
    #     up = ret > 0.
    #     skew = - amt[up].skew()
    #     return skew

    def calc_single(self, database):
        MinuteTurnover = database.depend_data["FactorData.Basic_factor.amt_minute"]
        MinuteVolume = database.depend_data["FactorData.Basic_factor.volume_minute"]
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        fmt = '%Y-%m-%d'
        date_list = sorted(np.unique(MinuteVolume.index.strftime(fmt)))
        compute_date = date_list[-1]
        pre_date = date_list[-2]
        
        amt = MinuteTurnover.loc[pre_date:compute_date].resample('5min').sum()
        volume = MinuteVolume.loc[pre_date:compute_date].resample('5min').sum()
        # ret = (amt / volume).pct_change()
        ret = amt/ volume
        ret = (ret - ret.shift(1))/ret
        up = pd.DataFrame(ret.values > 0., index=ret.index, columns=ret.columns)
        skew = - amt[up].skew()
        return skew

