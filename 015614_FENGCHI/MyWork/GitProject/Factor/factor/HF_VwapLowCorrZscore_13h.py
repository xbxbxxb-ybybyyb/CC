# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class HF_VwapLowCorrZscore_13h(BaseFactor):

    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.amt_minute",
    "FactorData.Basic_factor.low_minute"]
    lag = 0
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteAmt = database.depend_data['FactorData.Basic_factor.amt_minute']
        MinuteLow = database.depend_data['FactorData.Basic_factor.low_minute']
        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteAmt.index.strftime(fmt))

        date = date_list[-1]
        volume = MinuteVolume.loc[date]
        amt = MinuteAmt.loc[date]
        vwap = amt/volume
        low = MinuteLow.loc[date]
        ratio_df = (vwap / low).rank(axis=1)
        low_rank = low.rank(axis=1)
        corr = Util.array_coef(ratio_df,low_rank)
        return -corr

    def reform(self, temp_result):
        res = (temp_result-temp_result.rolling(self.reform_window,1).mean())/temp_result.rolling(self.reform_window,1).std()
        return res
