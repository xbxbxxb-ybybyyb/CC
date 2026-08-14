from xfactor.BaseFactor import BaseFactor
import pandas as pd
import numpy as np

class Re300ReturnScore5D(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_badj", "FactorData.Basic_factor.close-000300.SH", "FactorData.Basic_factor.is_valid"]
    lag = 1
    reform_window = 5

    def calc_single(self, database):
        close_adj = database.depend_data['FactorData.Basic_factor.close_badj']
        close_index = database.depend_data['FactorData.Basic_factor.close-000300.SH']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']

        ret_stock = close_adj.values[-1] / close_adj.values[0] - 1.
        ret_market = close_index.values[-1] / close_index.values[0] - 1.
        ans = ret_stock - ret_market
        ans = pd.Series(ans, index=close_adj.columns)
        ans[is_valid.iloc[-1]==0] = np.nan
        ans[~np.isfinite(ans)] = np.nan
        return ans

    def reform(self, temp_result):
        max_value = temp_result.rolling(self.reform_window).max()
        min_value = temp_result.rolling(self.reform_window).min()
        std_values =  temp_result.rolling(self.reform_window).std()
        alpha = (min_value + max_value) / std_values
        return - alpha