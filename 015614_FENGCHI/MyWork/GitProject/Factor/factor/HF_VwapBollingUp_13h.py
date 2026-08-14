# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class HF_VwapBollingUp_13h(BaseFactor):

    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.amt_minute"]
    lag = 0
    reform_window = 0

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteAmt = database.depend_data['FactorData.Basic_factor.amt_minute']
        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteAmt.index.strftime(fmt))

        date = date_list[-1]
        volume = MinuteVolume.loc[date]
        amt = MinuteAmt.loc[date]

        vwap = amt/volume
        
        rolling_mean = vwap.rolling(10,1).mean()
        rolling_std = vwap.rolling(10,1).std()
        diff = vwap.values - (rolling_mean.values + 2.*rolling_std.values)
        ratio = np.nansum(np.where(diff>0,diff,np.nan),axis=0) / np.nansum(2.*rolling_std.values,axis=0) 
        ratio[np.isnan(ratio).all()] = 0
        return pd.Series(-ratio,index=amt.columns)
