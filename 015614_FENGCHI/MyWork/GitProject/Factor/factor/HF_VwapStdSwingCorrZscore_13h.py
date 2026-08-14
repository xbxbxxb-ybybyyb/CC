# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform
import time

class HF_VwapStdSwingCorrZscore_13h(BaseFactor):

    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.amt_minute",
    "FactorData.Basic_factor.high_minute","FactorData.Basic_factor.low_minute"]
    lag = 0
    reform_window = 50

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteAmt = database.depend_data['FactorData.Basic_factor.amt_minute']
        MinuteHigh = database.depend_data['FactorData.Basic_factor.high_minute']
        MinuteLow = database.depend_data['FactorData.Basic_factor.low_minute']
        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteAmt.index.strftime(fmt))

        date = date_list[-1]

        swing = MinuteHigh.loc[date] - MinuteLow.loc[date]
        vwap = MinuteAmt.loc[date] / MinuteVolume.loc[date]
        corr = Util.array_coef(vwap.rolling(5,1).std(),swing)
        return -corr

    def reform(self, temp_result):
        res = (temp_result-temp_result.rolling(self.reform_window,1).mean())/temp_result.rolling(self.reform_window,1).std()
        return res