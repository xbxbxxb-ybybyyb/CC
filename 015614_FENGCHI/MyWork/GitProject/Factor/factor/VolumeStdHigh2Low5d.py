# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform,min_forward_adj
import time

class VolumeStdHigh2Low5d(BaseFactor):
    
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute",
                  "FactorData.Basic_factor.volume_minute"]


    lag = 0
    reform_window = 5

    def calc_single(self,database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        volume = database.depend_data['FactorData.Basic_factor.volume_minute']
        volume.iloc[0] = np.nan
        c_min = close.rolling(window=10,min_periods=8).min().values
        c_max = close.rolling(window=10,min_periods=8).max().values
        min_max = np.array([np.nanmax(c_min,axis=0)]*close.shape[0])
        max_min = np.array([np.nanmin(c_max,axis=0)]*close.shape[0])
        volume_high = np.where(close.values>=min_max,volume.values,np.nan)
        volume_low = np.where(close.values<=max_min,volume.values,np.nan)  
        result = np.nanstd(volume_high,axis=0)/np.nanstd(volume_low,axis=0)
        return pd.Series(-result,index=close.columns)
    
    
    def reform(self, temp_result):
        A = temp_result.rolling(self.reform_window, min_periods=1).mean()
        return A