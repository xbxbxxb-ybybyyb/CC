import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import xfactor.Util as Util

class PVMax(BaseFactor):
    s_high_min = 'FactorData.Basic_factor.high_minute'
    s_volume_min = 'FactorData.Basic_factor.volume_minute'
    depend_data = [s_high_min, s_volume_min]
    reform_window = 30

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=['drop', 'merge'])
        high = database.depend_data[self.s_high_min]
        volume = database.depend_data[self.s_volume_min]
        return Util.array_coef(high, volume)
    def weight(self,series,n):
        w = np.arange(1, (n + 1), 1) / n
        temp = (series * w).sum()
        return temp
    def reform(self, temp_result):
        factor_values = (-temp_result.rolling(20,10).max()).rank(axis=1, ascending=True)
        return factor_values.rolling(10).apply(self.weight,args=(10,))
