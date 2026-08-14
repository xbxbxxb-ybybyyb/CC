from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import pandas as pd

class UpCountLowDistance10d(BaseFactor):
    
    factor_type = "FIX"
    depend_data = [ 
                 "FactorData.Basic_factor.close_minute",]

    lag = 0
    minute_lag = 0
    reform_window= 10
    
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        close_minute = database.depend_data['FactorData.Basic_factor.close_minute']

        re = pd.DataFrame((close_minute.values/close_minute.shift(1).values-1)>0, index = close_minute.index,
                         columns = close_minute.columns)       
        return re.sum()/240
        
    
    def reform(self, temp_result):
        return -(temp_result - temp_result.rolling(window=self.reform_window).min())    

