# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MinReSkewLast120_10d(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.amt_minute"]
    lag = 0
    reform_window = 10

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteAmt = database.depend_data['FactorData.Basic_factor.amt_minute']

        price = MinuteAmt / MinuteVolume
        re = price/price.shift(1)
        result = -re.iloc[-120:].skew()

        return result
    
    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window,1).mean()