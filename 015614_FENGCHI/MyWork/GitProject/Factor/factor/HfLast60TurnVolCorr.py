from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class HfLast60TurnVolCorr(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.amt_minute", "FactorData.Basic_factor.volume_adj_minute"]
    lag = 1

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])        
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        volume = database.depend_data['FactorData.Basic_factor.volume_adj_minute']

        minute_volume = volume.values
        minute_amt = amt.values
        ans = self.array_coef(minute_volume[-60:], minute_amt[-60:])
        ans = pd.Series(ans, index=amt.columns)
        ans[~np.isfinite(ans)] = np.nan
        return ans

    def array_coef(self, x, y):
        x_values = x.astype(np.float64)
        y_values = y.astype(np.float64)
        x_values[np.isinf(x_values)] = np.nan
        y_values[np.isinf(y_values)] = np.nan
        nan_index = np.isnan(x_values) | np.isnan(y_values)
        x_values[nan_index] = np.nan
        y_values[nan_index] = np.nan
        delta_x = x_values - np.nanmean(x_values, axis=0)
        delta_y = y_values - np.nanmean(y_values, axis=0)
        multi = np.nanmean(delta_x * delta_y, axis=0) / (np.nanstd(delta_x, axis=0, ddof=1) * np.nanstd(delta_y, axis=0, ddof=1))
        multi[np.isinf(multi)] = np.nan
        return multi