# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform,min_forward_adj
import time

class HfLast120MaxRtnCloseCorrBias_13h(BaseFactor):

    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.high_adj_minute","FactorData.Basic_factor.close_adj_minute"]
    lag = 1
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteHigh = database.depend_data['FactorData.Basic_factor.high_adj_minute'][-125:]
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_adj_minute'][-125:]
        
        minute_max_5min = MinuteHigh.rolling(window=5,min_periods=1).max()
        minute_max_rtn = np.log(MinuteClose / minute_max_5min)

        df_factor = Util.array_coef(minute_max_rtn[-120:],MinuteClose[-120:])

        return df_factor

    def reform(self, temp_result):
        res = temp_result-temp_result.rolling(self.reform_window,1).mean()
        return res