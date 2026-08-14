from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class HighFreqDuoKongMeanBias(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.low_minute", 
                   "FactorData.Basic_factor.open_minute", "FactorData.Basic_factor.amt_minute"]
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])               
        high = database.depend_data['FactorData.Basic_factor.high_minute']
        low = database.depend_data['FactorData.Basic_factor.low_minute']
        open_df = database.depend_data['FactorData.Basic_factor.open_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']

        ret = (high.values - low.values) / open_df.values
        earn = ret * amt.values
        ans = np.nanmean(earn[-5:], axis=0)
        ans = pd.Series(ans, index=high.columns)
        ans[~np.isfinite(ans)] = np.nan
        return ans

    def reform(self, temp_result):
        return 1. - temp_result / temp_result.rolling(self.reform_window).mean()

