# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform
import time

class HF_VwapTailTRRatio_13h(BaseFactor):

    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.amt_minute",
    "FactorData.Basic_factor.high_minute","FactorData.Basic_factor.low_minute","FactorData.Basic_factor.close_minute"]
    lag = 0
    reform_window = 60

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteAmt = database.depend_data['FactorData.Basic_factor.amt_minute']
        MinuteLow = database.depend_data['FactorData.Basic_factor.low_minute']
        MinuteHigh = database.depend_data['FactorData.Basic_factor.high_minute']
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        fmt = '%Y%m%d'
        date_list = np.unique(MinuteAmt.index.strftime(fmt))
        compute_date = date_list[-1]
        
        high = MinuteHigh.loc[compute_date]
        low = MinuteLow.loc[compute_date]
        close = MinuteClose.loc[compute_date]
        TRH = np.maximum(high,close.shift(1))
        TRL = np.minimum(low,close.shift(1))
        TR = (TRH - TRL).values

        volume = MinuteVolume.loc[compute_date]
        amt = MinuteAmt.loc[compute_date]
        vwap = amt.values / volume.values             
        TR_tail = np.where(vwap<np.nanquantile(vwap,0.05,axis=0),TR,np.nan)
        ratio = np.nanmean(TR_tail,axis=0) / np.nanmean(TR,axis=0)

        return pd.Series(ratio,index=MinuteAmt.columns)

    def reform(self, temp_result):
        res = (temp_result-temp_result.rolling(self.reform_window,1).mean())/temp_result.rolling(self.reform_window,1).std()
        return res
