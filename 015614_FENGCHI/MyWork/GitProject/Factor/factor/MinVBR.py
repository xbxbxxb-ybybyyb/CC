from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np


class MinVBR(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.volume_minute",
                   "FactorData.Basic_factor.is_valid"]
    reform_window = 30

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        volume = database.depend_data['FactorData.Basic_factor.volume_minute']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']

        ma_volume = volume.rolling(window=10, min_periods=1).mean()
        vol_ratio = volume.values[1:] / ma_volume.values[:-1]
        ret = close.values[1:] / close.values[:-1] - 1.
        vol_burst = np.where(vol_ratio > 5, 1, 0)
        vol_burst_power = vol_burst * ret * volume.values[1:]
        ans = np.nansum(vol_burst_power, axis=0) / np.nansum(volume.values, axis=0)
        ans = pd.Series(ans, index=close.columns)
        ans[is_valid.iloc[-1] == 0] = np.nan
        ans[~np.isfinite(ans)] = np.nan
        return ans

    def weight(self,series):
        n = len(series)
        w = np.arange(1, (n + 1), 1) / n
        temp = (series * w).sum()
        return temp
    def reform(self, temp_result):
        temp_result = - temp_result.rolling(10).mean()
        return temp_result.rolling(20,5).apply(self.weight)