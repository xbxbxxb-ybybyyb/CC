from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class MinuteReturnAutocorr5d(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_adj_minute", "FactorData.Basic_factor.close_badj", "FactorData.Basic_factor.is_valid"]
    lag = 5
    fmt = '%Y-%m-%d'

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])        
        close = database.depend_data['FactorData.Basic_factor.close_adj_minute']
        close_adj = database.depend_data['FactorData.Basic_factor.close_badj']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']

        date_list = sorted(np.unique(close.index.strftime(self.fmt)))
        factor_list = []
        for date in date_list[1:]:
            close_date = close.loc[date]
            ret = close_date.values[1:] / close_date.values[:-1] - 1.
            corr = self.array_coef(ret[1:], ret[:-1])
            factor_list.append(corr)
        factor_list_array = np.stack(factor_list, axis=0)        
        factor = np.nanmean(factor_list_array, axis=0)
        factor_rank = pd.Series(factor, index=close.columns).rank(pct=True)

        ret_5d = close_adj.values[-1] / close_adj.values[0] - 1.
        ret_5d_rank = pd.Series(ret_5d, index=close.columns).rank(pct=True)

        ans = - factor_rank.values * ret_5d_rank.values
        ans = pd.Series(ans, index=close.columns)
        ans[is_valid.iloc[-1]==0] = np.nan
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
    