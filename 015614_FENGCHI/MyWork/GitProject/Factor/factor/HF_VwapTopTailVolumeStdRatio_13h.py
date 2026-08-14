# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform
import time

class HF_VwapTopTailVolumeStdRatio_13h(BaseFactor):

    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.amt_minute"]
    lag = 0
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteAmt = database.depend_data['FactorData.Basic_factor.amt_minute']
        fmt = '%Y%m%d'
        date_list = np.unique(MinuteAmt.index.strftime(fmt))
        date = date_list[-1]
        
        volume = MinuteVolume.loc[date]
        amt = MinuteAmt.loc[date]
        vwap = amt / volume
        volume_top = np.where(vwap.values>vwap.quantile(0.8).values,volume.values,np.nan)
        volume_tail = np.where(vwap.values<vwap.quantile(0.2).values,volume.values,np.nan)
        ratio = np.nanstd(volume_top,axis=0) / np.nanstd(volume_tail,axis=0)

        return pd.Series(-ratio,index=MinuteAmt.columns)

    def reform(self, temp_result):
        res = temp_result.rolling(self.reform_window,1).min()
        return res
