# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class Min60_RVstd(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute","FactorData.Basic_factor.open_minute",
    "FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.amt_minute"]
    lag = 0
    reform_window = 10

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        MinuteOpen = database.depend_data['FactorData.Basic_factor.open_minute']
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteAmt = database.depend_data['FactorData.Basic_factor.amt_minute']
        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))

        date = date_list[-1]
        close = MinuteClose.loc[date].values
        open_ = MinuteOpen.loc[date].values
        volume = MinuteVolume.loc[date].values
        amt = MinuteAmt.loc[date].values

        ret = close / open_ - 1
        RV = abs(ret) / volume
        RV60 = RV[-60:]
        amt60 = amt[-60:]
        volume60 = volume[-60:]
        RV_flag = RV60 > np.nanquantile(RV60,0.8,axis=0)
        
        vwap_60 = np.nansum(amt60,axis=0) / np.nansum(volume60,axis=0)

        amt60[~RV_flag] = np.nan
        volume60[~RV_flag] = np.nan
        vwap_RV = np.nansum(amt60,axis=0) / np.nansum(volume60,axis=0)


        return pd.Series(vwap_RV / vwap_60,index=MinuteClose.columns)


    def reform(self, temp_result):
        factor = temp_result.rolling(window=self.reform_window,min_periods=int(0.5*self.reform_window)).std()
        return -factor