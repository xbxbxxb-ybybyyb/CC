from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform

class MinTradeAmPmRatioMax20d(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.numtrade_minute"]

    lag = 0
    reform_window = 20

    def calc_single(self,database): 
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        numtrade_minute = database.depend_data['FactorData.Basic_factor.numtrade_minute']

        res = (numtrade_minute.iloc[:30].sum()+numtrade_minute.iloc[-30:].sum())/numtrade_minute.sum()

        return res
    
    def reform(self, temp_result):
        return -temp_result.rolling(self.reform_window,1).max()