from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import pandas as pd

class TwapSkewToVwap(BaseFactor):

    factor_type = "FIX"
    depend_data = [ 
                 "FactorData.Basic_factor.amt_minute",
                 "FactorData.Basic_factor.volume_minute",]

    lag = 0
    minute_lag = 0
    reform_window= 0
    
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        amt_minute = database.depend_data['FactorData.Basic_factor.amt_minute']
        volume_minute = database.depend_data['FactorData.Basic_factor.volume_minute']

        vwap = np.sum(amt_minute) / np.sum(volume_minute)
        price = amt_minute / volume_minute
        ratio = price.skew() / vwap
        
        return -ratio
        


    