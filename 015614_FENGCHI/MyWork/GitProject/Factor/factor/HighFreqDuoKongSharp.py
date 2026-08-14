from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class HighFreqDuoKongSharp(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.low_minute", 
                   "FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.amt_minute"]
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])               
        high = database.depend_data['FactorData.Basic_factor.high_minute']
        low = database.depend_data['FactorData.Basic_factor.low_minute']
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']

        ret = 2. * close.values / (high.values + low.values) - 1.
        earn = ret * amt.values
        ans = np.nanstd(earn, axis=0)
        ans = pd.Series(ans, index=close.columns)
        ans[~np.isfinite(ans)] = np.nan
        return ans

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean() / temp_result.rolling(self.reform_window).std()

