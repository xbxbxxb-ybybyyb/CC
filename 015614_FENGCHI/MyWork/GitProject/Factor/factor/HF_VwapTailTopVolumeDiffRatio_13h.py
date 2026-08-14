# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform,min_forward_adj
import time

class HF_VwapTailTopVolumeDiffRatio_13h(BaseFactor):

    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.volume_adj_minute","FactorData.Basic_factor.amt_minute"]
    lag = 1
    reform_window = 0

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteVolume =database.depend_data['FactorData.Basic_factor.volume_adj_minute']
        MinuteAmt = database.depend_data['FactorData.Basic_factor.amt_minute']
        
        volume = MinuteVolume.iloc[-30-120:]
        amt = MinuteAmt.iloc[-30-120:]
        vwap = amt.values / volume.values
        diff = volume.diff().abs().values
        diff_tail = np.where(vwap<np.nanquantile(vwap,0.05,axis=0),diff,np.nan)               
        diff_top = np.where(vwap>np.nanquantile(vwap,0.95,axis=0),diff,np.nan)
        ratio = np.nanmean(diff_tail,axis=0) / np.nanmean(diff_top,axis=0)
        ratio[np.isnan(ratio).all()] = 0.
        return pd.Series(ratio,index=MinuteAmt.columns)