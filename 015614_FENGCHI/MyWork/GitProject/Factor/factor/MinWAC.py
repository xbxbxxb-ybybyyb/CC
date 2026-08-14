import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
class MinWAC(BaseFactor):
    depend_data = ['FactorData.Basic_factor.high', 'FactorData.Basic_factor.volume']
    lag = 4
    reform_window = 20
    def calc_single(self, database):
        high = database.depend_data['FactorData.Basic_factor.high']
        vol = database.depend_data['FactorData.Basic_factor.volume']
        alpha = Util.array_coef(vol.rank(axis=1, pct=True), high.rank(axis=1, pct=True))
        alpha[np.isinf(alpha)] = np.nan
        return alpha.rank(ascending=False)
    def reform(self,temp_result):
        return temp_result.rolling(self.reform_window).apply(self.weight)
    def weight(self,series):
        weight = np.arange(1, (self.reform_window + 1), 1) / self.reform_window
        temp = (series * weight).sum()
        return temp