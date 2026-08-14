# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform,min_forward_adj
import time


class MinWR_20_80_5d(BaseFactor):
    factor_type = 'DAY' 
    depend_data = ['FactorData.Basic_factor.close_minute']   
    lag = 0
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        close = database.depend_data['FactorData.Basic_factor.close_minute']

        percent20 = np.nanquantile(close.values,0.2,axis=0)
        percent80 = np.nanquantile(close.values,0.8,axis=0)
        result = (close.values[-1]*2-percent20-percent80)/(percent80-percent20)

        return pd.Series(-result,index=close.columns)
    
    def reform(self, temp_result):
        A = temp_result.rolling(self.reform_window, min_periods=1).mean()
        return A
    
