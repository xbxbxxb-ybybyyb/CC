# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform
import time

class HF_VwapLowHighStdVolumeRatio_13h(BaseFactor):

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

        vwap = pd.DataFrame(np.nancumsum(amt.values,axis=0) / np.nancumsum(volume,axis=0),index=amt.index,columns=amt.columns)
        rolling_std = vwap.rolling(10).std().values
        volume_top = np.where(rolling_std > np.nanquantile(rolling_std,0.9,axis=0),volume,np.nan)
        volume_tail = np.where(rolling_std < np.nanquantile(rolling_std,0.1,axis=0),volume,np.nan)
        ratio_top = np.nansum(volume_top,axis=0) / np.nansum(volume,axis=0)
        ratio_tail = np.nansum(volume_tail,axis=0) / np.nansum(volume,axis=0)
        return pd.Series(ratio_tail / ratio_top,index=amt.columns)

    def reform(self, temp_result):
        res = temp_result/temp_result.rolling(window=self.reform_window,min_periods=1).max()
        res[np.isnan(res).all(axis=1)] = 0.
        return res

