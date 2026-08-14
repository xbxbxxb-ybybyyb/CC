from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class HfVolSkew(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.volume_adj_minute"]
    lag = 1
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])        
        volume = database.depend_data['FactorData.Basic_factor.volume_adj_minute']

        ans = - volume.rolling(window=5, min_periods=1).mean().skew()
        ans[~np.isfinite(ans)] = np.nan
        return ans

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean()