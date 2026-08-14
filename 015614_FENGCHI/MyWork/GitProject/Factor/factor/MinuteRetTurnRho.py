from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class MinuteRetTurnRho(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.amt_minute"]

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])        
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']

        t = amt.values
        c = close.values
        r = c[1:] / c[:-1] - 1.
        t_ma = np.nanmean(t[-5:], axis=0) / np.nanmean(t[-30:], axis=0)
        r_last = c[-1] / c[-31]
        corr = self.array_coef(t[-15:], r[-15:])
        t_norm = self.max_min_norm(t_ma)
        r_norm = self.max_min_norm(r_last)
        corr_norm = self.max_min_norm(corr)
        ans = - t_norm * r_norm * corr_norm
        ans = pd.Series(ans, index=close.columns)
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

    def max_min_norm(self, x):
        norm = ( x - np.nanmin(x)) / (np.nanmax(x) - np.nanmin(x))
        norm[np.isinf(norm)] = np.nan
        return norm