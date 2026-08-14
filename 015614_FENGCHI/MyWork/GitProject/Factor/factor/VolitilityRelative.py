from xfactor.BaseFactor import BaseFactor
import pandas as pd
import numpy as np

class VolitilityRelative(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_badj", "FactorData.Basic_factor.close-000985.CSI", "FactorData.Basic_factor.is_valid"]
    lag = 9
    reform_window = 10

    def calc_single(self, database):
        close_adj = database.depend_data['FactorData.Basic_factor.close_badj']
        close_index = database.depend_data['FactorData.Basic_factor.close-000985.CSI']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']

        ret_stock = (close_adj.values[-1] - np.nanmean(close_adj.values, axis=0)) / np.nanmean(close_adj.values, axis=0)
        ret_market = (close_index.values[-1] - np.nanmean(close_index.values, axis=0)) / np.nanmean(close_index.values, axis=0)
        ans = ret_stock / ret_market - 1.
        ans = pd.Series(ans, index=close_adj.columns)
        ans[is_valid.iloc[-1]==0] = np.nan
        ans[~np.isfinite(ans)] = np.nan
        return ans

    def reform(self, temp_result):
        alpha = - temp_result.rolling(self.reform_window).std() 
        return alpha