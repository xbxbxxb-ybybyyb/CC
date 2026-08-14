# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform,min_forward_adj
import time

class HfLast120CloseSwingStdCorrSharpe_13h(BaseFactor):

    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.high_adj_minute","FactorData.Basic_factor.close_adj_minute"
    ,"FactorData.Basic_factor.low_adj_minute"]
    lag = 1
    reform_window = 20

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteHigh = (database.depend_data['FactorData.Basic_factor.high_adj_minute'])[-125:]
        MinuteClose = (database.depend_data['FactorData.Basic_factor.close_adj_minute'])[-125:]
        MinuteLow = (database.depend_data['FactorData.Basic_factor.low_adj_minute'])[-125:]

        swing_std = (MinuteHigh/MinuteLow).rolling(5,1).std()
        df_factor = Util.array_coef(swing_std[-120:],MinuteClose[-120:])

        return -df_factor

    def reform(self, temp_result):
        res = temp_result.rolling(self.reform_window,1).mean()/temp_result.rolling(self.reform_window,1).std()
        return res

