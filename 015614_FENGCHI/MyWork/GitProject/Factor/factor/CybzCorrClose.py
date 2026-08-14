from xfactor.BaseFactor import BaseFactor
import pandas as pd
import numpy as np

class CybzCorrClose(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_badj", "FactorData.Basic_factor.close-399006.SZ"]
    lag = 20

    def calc_single(self, database):
        close_adj = database.depend_data['FactorData.Basic_factor.close_badj']
        close_index = database.depend_data['FactorData.Basic_factor.close-399006.SZ'] 

        ret_stock = close_adj.values[1:] / close_adj.values[:-1] - 1.
        ret_market = close_index.values[1:] / close_index.values[:-1] - 1.
        ans = self.array_series_corr(ret_stock, ret_market)
        ans = pd.Series(ans, index=close_adj.columns)
        ans[~np.isfinite(ans)] = np.nan
        return ans

    def array_series_corr(self, x, y):
        x_values = x.astype(np.float64)
        y_values = y.astype(np.float64)
        x_values[np.isinf(x_values)] = np.nan
        y_values[np.isinf(y_values)] = np.nan
        delta_x = x_values - np.nanmean(x_values, axis=0)
        delta_y = y_values - np.nanmean(y_values)
        multi = np.nanmean(delta_x * delta_y, axis=0) / (np.nanstd(delta_x, axis=0, ddof=1) * np.nanstd(delta_y, ddof=1))
        multi[np.isinf(multi)] = np.nan
        return multi