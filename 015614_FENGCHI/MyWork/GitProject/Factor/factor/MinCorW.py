import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import xfactor.Util as Util

class MinCorW(BaseFactor):
    depend_data = ["FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.low_minute",
                   "FactorData.Basic_factor.amt_minute", "FactorData.Basic_factor.volume_minute"]
    reform_window = 20

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=['drop', 'merge'])
        high = database.depend_data['FactorData.Basic_factor.high_minute']
        low = database.depend_data['FactorData.Basic_factor.low_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        vol = database.depend_data['FactorData.Basic_factor.volume_minute']
        p = (amt.rolling(15).sum() / vol.rolling(15).sum())[15:]
        d = (high.rolling(15).max() - low.rolling(15).min())[15:]
        corr = Util.array_coef(p, d)
        result = pd.Series(-corr, index=high.columns)
        return result.rank(pct=True)

    def reform(self, temp_result):
        temp_result = temp_result.rolling(5).min()
        return temp_result.rolling(10,5).apply(self.weight)

    def weight(self,series):
        n = len(series)
        w = np.arange(1, (n + 1), 1) / n
        temp = (series * w).sum()
        return temp