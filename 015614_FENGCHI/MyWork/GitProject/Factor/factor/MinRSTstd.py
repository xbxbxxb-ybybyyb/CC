# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MinRSTstd(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.high_minute","FactorData.Basic_factor.low_minute",
    "FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.amt_minute"]
    lag = 0
    reform_window = 10

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteHigh = database.depend_data['FactorData.Basic_factor.high_minute']
        MinuteLow = database.depend_data['FactorData.Basic_factor.low_minute']
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteAmt = database.depend_data['FactorData.Basic_factor.amt_minute']
        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteHigh.index.strftime(fmt))
        date = date_list[-1]

        high = MinuteHigh.loc[date]
        low = MinuteLow.loc[date]
        volume = MinuteVolume.loc[date]
        amt = MinuteAmt.loc[date]
        vwap = amt.values / volume.values
        vwap[~np.isfinite(vwap)] = np.nan
        hv_diff = high.values - vwap
        lv_diff = vwap - low.values
        price_ratio = high.values / vwap - 1
        vwap = pd.DataFrame(vwap,index=high.index,columns=high.columns)

        volume_rs = np.where(vwap.values > vwap.shift(1).values,volume.values,np.nan)
        volume_vrs = np.where(volume_rs>=np.nanquantile(volume_rs,0.9,axis=0),volume_rs,np.nan)
        price_ratio_vrs = np.where(volume_rs>=np.nanquantile(volume_rs,0.9,axis=0),price_ratio,np.nan)
        res = np.nansum(volume_vrs*price_ratio_vrs/np.nansum(volume_vrs,axis=0),axis=0)

        return pd.Series(res,index=high.columns)

    def reform(self, temp_result):
        return -temp_result.rolling(window=self.reform_window,min_periods=int(0.5*self.reform_window)).std()
     