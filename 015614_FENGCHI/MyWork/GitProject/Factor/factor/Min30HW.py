from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np


class Min30HW(BaseFactor):
    depend_data = ['FactorData.Basic_factor.volume_minute']
    lag = 4
    reform_window = 10
    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        vol = database.depend_data['FactorData.Basic_factor.volume_minute']
        stk_code = vol.columns
        vol = vol.resample('30min').sum().dropna(how='all').values
        result = np.nansum((vol / np.nansum(vol, axis=0)) ** 2, axis=0)
        result = pd.Series(-result, index=stk_code)
        return result.rank(pct=True)

    def weight(self,series):
        n = len(series)
        w = np.arange(1, (n + 1), 1) / n
        temp = (series * w).sum()
        return temp
    def reform(self, temp_result):
        return temp_result.rolling(10,5).apply(self.weight)