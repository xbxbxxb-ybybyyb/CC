# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform,min_forward_adj
import time

class HfAmtSpaceSkewMean_13h(BaseFactor):

    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.high_adj_minute",
    "FactorData.Basic_factor.low_adj_minute",
    "FactorData.Basic_factor.volume_adj_minute"]
    lag = 1
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteHigh = (database.depend_data['FactorData.Basic_factor.high_adj_minute'])[-240:]
        MinuteLow = (database.depend_data['FactorData.Basic_factor.low_adj_minute'])[-240:]
        MinuteVolume = (database.depend_data['FactorData.Basic_factor.volume_adj_minute'])[-240:]

        minute_amt_space = (MinuteHigh-MinuteLow) * MinuteVolume
        df_factor = -minute_amt_space.rolling(window=5,min_periods=1).mean().skew()
        return pd.Series(df_factor,index=MinuteHigh.columns)


    def reform(self, temp_result):
        res = temp_result.rolling(self.reform_window,1).mean()
        return res


