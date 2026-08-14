from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import pandas as pd

class MinuteLastHourSkewness40d(BaseFactor):
    
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute"]


    lag = 0
    reform_window = 40
    
    def calc_single(self, database):
    
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        close_minute = database.depend_data['FactorData.Basic_factor.close_minute']

        re = close_minute.values / close_minute.shift(1).values - 1
        re = pd.DataFrame(re, index = close_minute.index, columns=close_minute.columns)        
        result = re[-60:].skew()
        return -result

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window, min_periods = 1).mean()
    
    