from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import copy
import time
from sklearn.preprocessing import scale

class VolRaiseMom5d(BaseFactor):
    
    factor_type = "DAY"
    depend_data = [ 
    
                    "FactorData.Basic_factor.volume_minute",
                    "FactorData.Basic_factor.close_minute",    
                    ]

    lag = 10
    minute_lag = 10
    reform_window = 5
    
    def calc_single(self, database):
    
        volume_minute = database.depend_data['FactorData.Basic_factor.volume_minute']
        close_minute = database.depend_data['FactorData.Basic_factor.close_minute']

        datelist = sorted(close_minute.index.strftime('%Y%m%d').unique())
        pre_volume_minute = volume_minute.loc[:datelist[-2]]
        pre_volume_minute['time'] = pre_volume_minute.index.strftime('%H%M%S')
        pre_volume_minute = pre_volume_minute.set_index('time').groupby('time').mean()
        
        today_volume = volume_minute.loc[datelist[-1]]
        today_volume['time'] = today_volume.index.strftime('%H%M%S')
        today_volume = today_volume.set_index('time') 

        today_close = close_minute.loc[datelist[-1]]
        today_close['time'] = today_close.index.strftime('%H%M%S')
        today_close = today_close.set_index('time') 

        liangbi = today_volume/pre_volume_minute

        today_re = (today_close-today_close.shift(1))/today_close.shift(1)
        compound = today_re*liangbi
        return -compound.mean()
        
        
     
    def reform(self,temp_result):
        factor = temp_result
        res = factor.rolling(self.reform_window,1).mean() 
        return res
    



