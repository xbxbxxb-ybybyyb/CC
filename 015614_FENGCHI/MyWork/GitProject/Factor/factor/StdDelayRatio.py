from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import pandas as pd

class StdDelayRatio(BaseFactor):
    
    factor_type = "FIX"
    depend_data = [ 
                 "FactorData.Basic_factor.close_adj_minute"]

    lag = 5
    minute_lag = 1
    
    def calc_single(self, database):
    
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        close_adj_minute = database.depend_data['FactorData.Basic_factor.close_adj_minute']

        # date_list = sorted(np.unique(close_adj_minute.index.strftime('%Y%m%d')))
        # date = date_list[-1]

        MinuteDelay = close_adj_minute.shift(10)
        CloseStd = close_adj_minute.rolling(30).std()
        DelayStd = MinuteDelay.rolling(30).std()
        f = -CloseStd / DelayStd
        return f.skew()
    
        