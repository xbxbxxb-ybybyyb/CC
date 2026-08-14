# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform
import time

class HF_VwapTopVolumeRatioZscore_13h(BaseFactor):

    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.amt_minute"]
    lag = 0
    reform_window = 10

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteAmt = database.depend_data['FactorData.Basic_factor.amt_minute']
        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteAmt.index.strftime(fmt))

        date = date_list[-1]      
        volume = MinuteVolume.loc[date].values
        amt = MinuteAmt.loc[date].values
        vwap = amt/volume
        vol_top = np.where(vwap>np.nanquantile(vwap,0.9,axis=0),volume,np.nan)
        ratio = np.nansum(vol_top,axis=0) / np.nansum(volume,axis=0)
        
        return pd.Series(-ratio,index=MinuteAmt.columns)

    def reform(self, temp_result):
        res = (temp_result-temp_result.rolling(self.reform_window,1).mean())/temp_result.rolling(self.reform_window,1).std()
        res.fillna(0.,inplace=True)
        return res