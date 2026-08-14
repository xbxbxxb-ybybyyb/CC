from xfactor.BaseFactor import BaseFactor
import pandas as pd
import numpy as np

class TurnCorrSharp(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_badj", "FactorData.Basic_factor.free_turn", "FactorData.Basic_factor.is_valid"]
    lag = 10
    reform_window = 10

    def calc_single(self, database):
        close_adj = database.depend_data['FactorData.Basic_factor.close_badj']
        turn = database.depend_data['FactorData.Basic_factor.free_turn']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']

        ret = close_adj.values[1:] / close_adj.values[:-1] - 1.
        turn_shift = turn.values[:-1]
        ans = self.array_coef(ret, turn_shift)       
        ans = pd.Series(ans, index=close_adj.columns)
        ans[is_valid.iloc[-1]==0] = np.nan
        ans[~np.isfinite(ans)] = np.nan
        return ans

    def reform(self, temp_result):
        alpha = temp_result.rolling(self.reform_window).mean() / temp_result.rolling(self.reform_window).std()
        return alpha

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
        
    
            