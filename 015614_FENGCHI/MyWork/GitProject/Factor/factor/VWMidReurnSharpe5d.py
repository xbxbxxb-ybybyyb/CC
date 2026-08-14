from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
from xfactor.FixUtil import min_forward_adj
import pandas as pd

class VWMidReurnSharpe5d(BaseFactor):

    factor_type = "FIX"

    depend_data = [ 
                 "FactorData.Basic_factor.high_adj_minute",
                 "FactorData.Basic_factor.low_adj_minute",
                 "FactorData.Basic_factor.volume_adj_minute",
                "FactorData.Basic_factor.close_adj_minute",]

    minute_lag = 1
    reform_window=5
    
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        high_minute = database.depend_data['FactorData.Basic_factor.high_adj_minute']
        low_minute = database.depend_data['FactorData.Basic_factor.low_adj_minute']
        volume_minute = database.depend_data['FactorData.Basic_factor.volume_adj_minute']
        close_minute = database.depend_data['FactorData.Basic_factor.close_adj_minute']
        
        mid = pd.DataFrame((high_minute.values+low_minute.values)/2, index=low_minute.index, columns =low_minute.columns)
        mid_re = pd.DataFrame(mid.values/mid.shift(1).values-1, index = mid.index, columns=mid.columns)
        tmp = pd.DataFrame(volume_minute.values/volume_minute.sum().values,index =volume_minute.index,columns=volume_minute.columns)
        result = (tmp*mid_re).sum()
        return result
    
      
    def reform(self, temp_result):
        return -(temp_result.rolling(window=self.reform_window,min_periods=1).mean()/temp_result.rolling(window=self.reform_window,min_periods=1).std())    

