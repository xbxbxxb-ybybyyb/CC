from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform,min_forward_adj

class Aktr(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.amt_minute"]
    lag=0
    reform_window=60
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop1", "drop4"])
        minute_amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        ans = minute_amt.std()
        return ans

    def reform(self, temp_result):
        temp_result = temp_result.rolling(20, min_periods=1).std()/temp_result.rolling(10, min_periods=1).mean()
        return -1*temp_result.rank(axis=1).rolling(10).apply(lambda x:self.weight(x,10))

    def weight(self,series,n=20):
        weight = np.arange(1, (n + 1), 1) / n
        temp = (series * weight).sum()
        return temp
