from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class HighFreqDrawBack(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.close_minute"]

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])        
        close = database.depend_data['FactorData.Basic_factor.close_minute']

        ret = close.values[1:] / close.values[:-1] - 1.
        ans = 1. - ret[-1] / np.nanmax(ret, axis=0)
        ans = pd.Series(ans, index=close.columns)
        ans[~np.isfinite(ans)] = np.nan
        return ans

