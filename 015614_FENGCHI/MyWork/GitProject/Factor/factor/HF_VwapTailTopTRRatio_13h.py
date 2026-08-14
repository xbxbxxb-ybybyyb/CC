# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform
import time

class HF_VwapTailTopTRRatio_13h(BaseFactor):

    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.amt_minute",
    "FactorData.Basic_factor.high_minute","FactorData.Basic_factor.low_minute","FactorData.Basic_factor.close_minute"]
    lag = 0
    reform_window = 20

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteAmt = database.depend_data['FactorData.Basic_factor.amt_minute']
        MinuteHigh = database.depend_data['FactorData.Basic_factor.high_minute']
        MinuteLow = database.depend_data['FactorData.Basic_factor.low_minute']
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteAmt.index.strftime(fmt))

        date = date_list[-1]

        high = MinuteHigh.loc[date]
        low = MinuteLow.loc[date]
        close = MinuteClose.loc[date]
        TRH = np.maximum(high.values,close.shift(1).values)
        TRL = np.minimum(low.values,close.shift(1).values)
        TR = TRH - TRL       
        volume = MinuteVolume.loc[date]
        amt = MinuteAmt.loc[date]
        vwap = amt.values / volume.values
        TR_top = np.where(vwap > np.nanquantile(vwap,0.95,axis=0),TR,np.nan)
        TR_tail = np.where(vwap < np.nanquantile(vwap,0.05,axis=0),TR,np.nan)
        ratio = np.nanmean(TR_tail,axis=0) / np.nanmean(TR_top,axis=0)
        
        return pd.Series(ratio,index=high.columns)

    def reform(self, temp_result):
        res = temp_result-temp_result.rolling(self.reform_window,1).mean()
        return res
