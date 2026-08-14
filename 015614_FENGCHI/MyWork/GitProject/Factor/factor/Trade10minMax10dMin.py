# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform,min_forward_adj
import time

class Trade10minMax10dMin(BaseFactor):
    
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute",
                  "FactorData.Basic_factor.numtrade_minute"]


    lag = 0
    reform_window = 10

    def calc_single(self,database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        numtrade = database.depend_data['FactorData.Basic_factor.numtrade_minute']

        trade_max = numtrade.rolling(10,1).sum().max()/numtrade.sum()
        return pd.Series(trade_max,index=close.columns)
    
    
    def reform(self, temp_result):
        A = -temp_result.rolling(self.reform_window, min_periods=1).min()
        return A