from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import copy
import time
from sklearn.preprocessing import scale

class CancelRateStd20d(BaseFactor):
    
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.sellordervol_minute",
                    "FactorData.Basic_factor.buyordervol_minute",
                    "FactorData.Basic_factor.buyordercanceledvol_minute",
                    "FactorData.Basic_factor.sellordercanceledvol_minute",
    
                    ]

    lag = 0
    minute_lag = 0
    reform_window = 20
    
    def calc_single(self, database):
    
        sellordervol_minute = database.depend_data['FactorData.Basic_factor.sellordervol_minute']
        buyordervol_minute = database.depend_data['FactorData.Basic_factor.buyordervol_minute']
        buyordercanceledvol_minute = database.depend_data['FactorData.Basic_factor.buyordercanceledvol_minute']
        sellordercanceledvol_minute = database.depend_data['FactorData.Basic_factor.sellordercanceledvol_minute']
      
        cancel_rate = (sellordercanceledvol_minute+buyordercanceledvol_minute)/(sellordervol_minute+buyordervol_minute)

        return cancel_rate.std()
      
     
    def reform(self,temp_result):
        factor = temp_result
        res = factor.rolling(self.reform_window,1).mean() 
        return res
    