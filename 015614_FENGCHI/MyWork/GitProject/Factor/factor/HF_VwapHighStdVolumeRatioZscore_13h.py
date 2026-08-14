# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class HF_VwapHighStdVolumeRatioZscore_13h(BaseFactor):

    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.amt_minute"]
    lag = 0
    reform_window = 20

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteAmt = database.depend_data['FactorData.Basic_factor.amt_minute']
        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteAmt.index.strftime(fmt))

        date = date_list[-1]
        volume = MinuteVolume.loc[date].values
        amt = MinuteAmt.loc[date]
        volume[volume==0.] = np.nan
        vwap = pd.DataFrame(amt.values / volume,index=amt.index,columns=amt.columns)
        rolling_std = vwap.rolling(10,1).std()
        volume_top = np.where(rolling_std.values > np.nanquantile(rolling_std.values,0.9,axis=0),volume,np.nan)
        ratio_top = np.nansum(volume_top,axis=0) / np.nansum(volume,axis=0)
        return pd.Series(-ratio_top,index=amt.columns)

    def reform(self, temp_result):
        res = (temp_result-temp_result.rolling(self.reform_window,1).mean())/temp_result.rolling(self.reform_window,1).std()
        res[np.isnan(res).all(axis=1)] = 0.
        return res