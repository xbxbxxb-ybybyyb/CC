from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import pandas as pd

class TrendStrength(BaseFactor):
    
    factor_type = "FIX"
    depend_data = [ 
                 "FactorData.Basic_factor.close_minute",]

    lag = 5
    minute_lag = 1
    reform_window = 5

    def calc_single(self, database):
    
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        close_minute = database.depend_data['FactorData.Basic_factor.close_minute']
        fmt = '%Y%m%d'
        date_list = np.unique(close_minute.index.strftime(fmt))

        date = date_list[-1]
        pre_date = date_list[-2]
        closedf = close_minute[pre_date].iloc[-30:]
        closedf_today = close_minute[date].iloc[:5]
        ret = (closedf.iloc[-1] - closedf.iloc[0]) / closedf.iloc[0] + (closedf_today.iloc[0] - closedf_today.iloc[-1]) / closedf_today.iloc[0]
        ret_1m = (abs(closedf - closedf.shift(1))).sum()
        ratio = -ret / ret_1m

        return ratio
    
        
    
    def reform(self, temp_result):
        n = self.reform_window
        seq = [(1-(2.0/(n+1))) ** (n-i) for i in range(1, n + 1)]
        weight = np.array(seq)
        weight_sum = np.sum(weight)

        return temp_result.rolling(window=self.reform_window).apply(lambda x: np.sum(x * weight) / weight_sum)


    