from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np


class MinPmR(BaseFactor):
    factor_type = "DAY"
    s_open_min = 'FactorData.Basic_factor.open_minute'
    s_close_min = 'FactorData.Basic_factor.close_minute'
    depend_data = [s_open_min, s_close_min]
    reform_window = 20

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=['drop', 'merge'])
        open_min = database.depend_data[self.s_open_min]
        close_min = database.depend_data[self.s_close_min]
        return self.calc_ratio(open_min, close_min)

    def reform(self, temp_result):
        temp_result[np.isinf(temp_result)] = np.nan
        temp_result[np.isnan(temp_result)] = 0
        return temp_result.rolling(20, 5).apply(self.weight)
    def weight(self,series):
        n = len(series)
        w = np.arange(1, (n + 1), 1) / n
        temp = (series * w).sum()
        return temp
    def calc_ratio(self, minute_open, minute_close):
        _open = minute_open[120:]
        close = minute_close[120:]

        diff = close - _open
        diff_abs = np.abs(diff)
        diff_up = (diff_abs + diff) / 2
        diff_up[pd.DataFrame(diff_up.values == 0, index=diff_up.index, columns=diff_up.columns)] = np.nan
        diff_down = (diff_abs - diff) / 2
        diff_down[pd.DataFrame(diff_down.values == 0, index=diff_down.index, columns=diff_down.columns)] = np.nan

        up = diff_up.mean()
        down = diff_down.mean()

        ratio = down / up

        return ratio

