# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform,min_forward_adj
import time

class ReStdUp2Down5d(BaseFactor):
    
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute"]


    lag = 0
    reform_window = 5

    def calc_single(self,database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        close = database.depend_data['FactorData.Basic_factor.close_minute']

        re = (close/close.shift(1)).values-1
        re_mean = np.nanmean(re,axis=0)

        down = np.where(re<re_mean,re,np.nan)
        up = np.where(re>re_mean,re,np.nan)
        ReStdUp2Down = np.nanstd(up,axis=0)/np.nanstd(down,axis=0)
        
        return pd.Series(-ReStdUp2Down,index=close.columns)
    
    def reform(self, temp_result):
        A = temp_result.rolling(self.reform_window, min_periods=1).mean()
        return A