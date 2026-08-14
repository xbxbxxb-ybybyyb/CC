# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MinuteVMASkew(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.volume_minute"]
    lag = 0
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteVolume.index.strftime(fmt))

        date = date_list[-1]
        volume = MinuteVolume.loc[date]
        res = -volume.rolling(10).mean().skew()

        return res

    def reform(self, temp_result):
        return temp_result.rolling(window=self.reform_window,min_periods=1).mean()