from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import pandas as pd

class SwingPriceCorr(BaseFactor):
    
    factor_type = "FIX"
    depend_data = [ 
                 "FactorData.Basic_factor.low_minute",
                 "FactorData.Basic_factor.high_minute",
                 "FactorData.Basic_factor.volume_minute",
                 "FactorData.Basic_factor.amt_minute"]

    lag = 5
    minute_lag = 0
    
    def calc_single(self, database):
    
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        volume_minute = database.depend_data['FactorData.Basic_factor.volume_minute']
        high_minute = database.depend_data['FactorData.Basic_factor.high_minute']
        low_minute = database.depend_data['FactorData.Basic_factor.low_minute']
        amt_minute = database.depend_data['FactorData.Basic_factor.amt_minute']
        
        today_price = amt_minute / volume_minute
        swing = (high_minute - low_minute) / low_minute
        
        corr = Util.array_coef(today_price, swing)
        
        return -corr
    
        