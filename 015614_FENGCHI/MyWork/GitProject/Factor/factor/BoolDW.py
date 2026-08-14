from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform, min_forward_adj


class BoolDW(BaseFactor):
    
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute"]
    lag = 0
    reform_window = 30
    def calc_single(self, database):
    
        minute_data_transform(database.depend_data, operation=["drop1", "drop4"])
        minute_close = database.depend_data['FactorData.Basic_factor.close_minute']
        minute_close = min_forward_adj(minute_close)
        close_mean = minute_close.rolling(window=10, min_periods=1).mean()
        close_std = minute_close.rolling(window=10, min_periods=1).std()
        bool_up = close_mean + 2 * close_std
        up_pct = minute_close[minute_close > bool_up] / bool_up - 1
        up_pct_sum = up_pct.sum(axis=0)
        bool_down = close_mean - 2 * close_std
        down_pct = minute_close[minute_close < bool_down] / bool_down - 1
        down_pct_sum = down_pct.sum(axis=0)
        ans = up_pct_sum + down_pct_sum
        return ans

    def reform(self, temp_result):
        temp_result[np.isinf(temp_result)] = np.nan
        temp_result[np.isnan(temp_result)] = 0
        temp_result = temp_result.rolling(10).mean()
        return -temp_result.rolling(20, 5).apply(self.weight)
    def weight(self,series):
        n = len(series)
        w = np.arange(1, (n + 1), 1) / n
        temp = (series * w).sum()
        return temp

