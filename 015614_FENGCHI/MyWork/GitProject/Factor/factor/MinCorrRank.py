from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class MinCorrRank(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.amt", "FactorData.Basic_factor.volume", "FactorData.Basic_factor.adjfactor",
                   "FactorData.Basic_factor.close_adj_minute", "FactorData.Basic_factor.volume_adj_minute"]
    lag = 4
    fmt = '%Y-%m-%d'

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])
        amt_day = database.depend_data['FactorData.Basic_factor.amt']
        volume_day = database.depend_data['FactorData.Basic_factor.volume']
        adjfactor = database.depend_data['FactorData.Basic_factor.adjfactor']
        close = database.depend_data['FactorData.Basic_factor.close_adj_minute']
        volume = database.depend_data['FactorData.Basic_factor.volume_adj_minute']

        date_list = np.unique(volume.index.strftime(self.fmt))
        volume_date = volume.loc[date_list[-1]]
        close_date = close.loc[date_list[-1]]

        volume_last = np.nansum(volume_date.values[-10:], axis=0) / np.nansum(volume_date.values[-30:], axis=0)
        volume_last_rank = pd.Series(volume_last, index=close.columns).rank(pct=True)
        vol_close_corr = self.array_coef(close_date.values[-10:], volume_date.values[-10:])
        vol_close_corr_rank = pd.Series(vol_close_corr, index=close.columns).rank(pct=True)    
        min_result = vol_close_corr_rank.values * volume_last_rank.values

        volume_day = volume_day.replace(0., np.nan)
        vwap_adj = amt_day.values / volume_day.values * adjfactor.values 
        vwap_vol_corr = self.array_coef(vwap_adj, volume_day.values)
        vwap_vol_corr_rank = pd.Series(vwap_vol_corr,index=close.columns).rank(pct=True)
        ans = - vwap_vol_corr_rank.values * min_result     
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