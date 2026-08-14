from xfactor.BaseFactor import BaseFactor
import pandas as pd
import numpy as np

class AmtStdBias(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.amt","FactorData.Basic_factor.is_valid"]
    lag = 19
    reform_window = 20

    def calc_single(self, database):
        amt = database.depend_data['FactorData.Basic_factor.amt']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']

        ans = np.nanstd(amt.values, axis=0, ddof=1)        
        ans = 1. / ans * 10**6
        ans = pd.Series(ans, index=amt.columns)
        ans[is_valid.iloc[-1]==0] = np.nan
        ans[~np.isfinite(ans)] = np.nan
        return ans

    def reform(self, temp_result):
        alpha = temp_result - temp_result.rolling(self.reform_window).mean() 
        return alpha



