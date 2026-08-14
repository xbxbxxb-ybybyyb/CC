from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import pandas as pd

class SwingReturn(BaseFactor):
    
    factor_type = "FIX"
    depend_data = [ 
                 "FactorData.Basic_factor.low_minute",
                 "FactorData.Basic_factor.high_minute",
                 "FactorData.Basic_factor.close_minute",]

    minute_lag = 0

    def calc_single(self, database):
    
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        high_minute = database.depend_data['FactorData.Basic_factor.high_minute']
        low_minute = database.depend_data['FactorData.Basic_factor.low_minute']
        close_minute = database.depend_data['FactorData.Basic_factor.close_minute']
           
        ratio = close_minute.iloc[-60:].mean() / close_minute.mean()
        swing = ((high_minute - low_minute) / low_minute).mean()
        
        result = -ratio * np.log(swing)
        return result
