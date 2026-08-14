# -*- coding: utf-8 -*-

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
import time
from xfactor.FixUtil import minute_data_transform

class CloseVolatility5d(BaseFactor):
    
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute"]
    lag = 0
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        re = close/close.shift(1)
        ClosePercent = close.rank(axis=0,pct=True).iloc[-1]
        Vol = re.std()
        return -ClosePercent*Vol

    def reform(self, temp_result):
        A = temp_result.rolling(self.reform_window, min_periods=1).mean()
        return A