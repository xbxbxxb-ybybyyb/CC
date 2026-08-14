from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import pandas as pd

class MinuteCloseWRVolume(BaseFactor):

    
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute", 
                   "FactorData.Basic_factor.high_minute", 
                   "FactorData.Basic_factor.low_minute", 
                   "FactorData.Basic_factor.volume_minute",
                "FactorData.Basic_factor.is_valid", ]
    lag = 0
    
    def calc_single(self, database):
    
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        volume_minute = database.depend_data['FactorData.Basic_factor.volume_minute']
        close_minute = database.depend_data['FactorData.Basic_factor.close_minute']
        low_minute = database.depend_data['FactorData.Basic_factor.low_minute']
        high_minute = database.depend_data['FactorData.Basic_factor.high_minute']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']
        valid = pd.DataFrame(is_valid.values==1, index=is_valid.index, columns=is_valid.columns)
        
        high = high_minute[-10:].max()
        low = low_minute[-10:].min()
        close = close_minute.iloc[-1]
        adj2 = Util.array_coef(close_minute[-10:], volume_minute[-10:])


        result = (high - close)/(high - low)*(1-adj2)   
        result[np.isinf(result)] = 0
        return result[valid.iloc[-1]]