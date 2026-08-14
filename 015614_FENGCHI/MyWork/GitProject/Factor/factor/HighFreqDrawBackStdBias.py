from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class HighFreqDrawBackStdBias(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.high_minute"]
    reform_window = 10

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])        
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        high = database.depend_data['FactorData.Basic_factor.high_minute']

        ans = np.nanstd(close.values / high.values - 1., axis=0)
        ans = pd.Series(ans, index=close.columns)
        ans[~np.isfinite(ans)] = np.nan
        return ans

    def reform(self, temp_result):
        return 1. - temp_result / temp_result.rolling(self.reform_window).mean()

