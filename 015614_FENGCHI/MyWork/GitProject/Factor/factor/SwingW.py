# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np

class SwingW(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.swing", "FactorData.Basic_factor.low", "FactorData.Basic_factor.high"]
    lag = 5
    reform_window = 20
    def calc_single(self, database):
        n = 5
        low = database.depend_data['FactorData.Basic_factor.low']
        high = database.depend_data['FactorData.Basic_factor.high']
        swing = database.depend_data['FactorData.Basic_factor.swing']
        corr_high = Util.array_coef(swing.iloc[-n:], high.iloc[-n:])
        corr_low = Util.array_coef(swing.iloc[-n:], low.iloc[-n:])
        result = corr_high + corr_low
        result[np.isinf(result)] = np.nan
        return -result
    def reform(self, temp_result):
        return temp_result.rolling(20, 5).apply(self.weight)
    def weight(self,series):
        n = len(series)
        w = np.arange(1, (n + 1), 1) / n
        temp = (series * w).sum()
        return temp



