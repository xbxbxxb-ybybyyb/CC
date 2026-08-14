from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import pandas as pd

class StdUpDown(BaseFactor):
    
    factor_type = "FIX"
    depend_data = [ 
                  "FactorData.Basic_factor.close_adj_minute"]

    lag = 1
    minute_lag = 1
    
    def calc_single(self, database):
    
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        close_minute = database.depend_data['FactorData.Basic_factor.close_adj_minute']

        re = pd.DataFrame(close_minute.values/close_minute.shift(1).values-1, index = close_minute.index, columns = close_minute.columns)
        std = re.rolling(30).std()
        
        diff = pd.DataFrame(close_minute.values-close_minute.shift(1).values, index = close_minute.index, columns = close_minute.columns)
        condi1 = pd.DataFrame(diff.values<0, index = diff.index, columns=diff.columns)
        condi2 = pd.DataFrame(diff.values>0, index = diff.index, columns=diff.columns)
        DO_pct_change = std * (condi1)
        UP_pct_change = std * (condi2)
        UP_Value = UP_pct_change.sum()/std.sum()
        DO_Value = DO_pct_change.sum()/std.sum()
        
        return -DO_Value/UP_Value
        
    
        