from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import copy
import time
from sklearn.preprocessing import scale



class AmtPerTradeReSkew20d(BaseFactor):
    
    factor_type = "DAY"
    depend_data = [ 'FactorData.Basic_factor.close_minute',
                    'FactorData.Basic_factor.amt_minute',
                    'FactorData.Basic_factor.numtrade_minute']
                    

    minute_lag = 0
    lag = 0
    reform_window = 20

    def calc_single(self, database):

        amt_minute = database.depend_data['FactorData.Basic_factor.amt_minute']
        close_minute = database.depend_data['FactorData.Basic_factor.close_minute']
        numtrade_minute = database.depend_data['FactorData.Basic_factor.numtrade_minute']

        re = (close_minute-close_minute.shift(1))/close_minute.shift(1)
        amtpertrade = amt_minute/ numtrade_minute
         
        return  -(amtpertrade*re).skew()
        
        
        
    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window, min_periods = 1).mean()    
        