from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import pandas as pd

class SwingPriceShortCorr(BaseFactor):

    
    factor_type = "FIX"
    depend_data = [ 
                 "FactorData.Basic_factor.low_minute",
                 "FactorData.Basic_factor.high_minute",
                 "FactorData.Basic_factor.open_minute",
                 "FactorData.Basic_factor.close_minute",
                 "FactorData.Basic_factor.volume_minute",
                 "FactorData.Basic_factor.amt_minute"]

    lag = 5
    minute_lag = 0
    reform_window = 20

    def calc_single(self, database):
    
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        volume_minute = database.depend_data['FactorData.Basic_factor.volume_minute']
        high_minute = database.depend_data['FactorData.Basic_factor.high_minute']
        low_minute = database.depend_data['FactorData.Basic_factor.low_minute']
        amt_minute = database.depend_data['FactorData.Basic_factor.amt_minute']
        open_minute = database.depend_data['FactorData.Basic_factor.open_minute']
        close_minute = database.depend_data['FactorData.Basic_factor.close_minute']
        
        price_diff = (close_minute - open_minute).values
        price_diff[price_diff>=0] = 1
        price_diff[price_diff<0] = -1
        
        today_price = amt_minute / volume_minute
        swing = (high_minute - low_minute) / low_minute
        
        price_diff = pd.DataFrame(price_diff, index=close_minute.index, columns=close_minute.columns)
        condi =  pd.DataFrame(price_diff.values==-1, index=close_minute.index, columns=close_minute.columns)
        
        corr = Util.array_coef(today_price* price_diff[condi], swing * price_diff[condi])
        
        return -corr
    
    def reform(self, temp_result):
        return temp_result.rolling(window=self.reform_window, min_periods = 19).mean() 