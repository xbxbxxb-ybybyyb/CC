from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform


class MinVolM(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.buytradeamt_minute"]

    lag = 0
    reform_window = 10

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        numtrade_minute = database.depend_data['FactorData.Basic_factor.buytradeamt_minute']

        res = numtrade_minute.rolling(10, 1).sum().max() / numtrade_minute.sum()

        return -res

    def weight(self,series):
        n = len(series)
        w = np.arange(1, (n + 1), 1) / n
        temp = (series * w).sum()
        return temp
    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window,1).apply(self.weight)