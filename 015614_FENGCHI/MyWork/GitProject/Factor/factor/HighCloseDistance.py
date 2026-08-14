from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class HighCloseDistance(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.high_minute"]

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])        
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        high = database.depend_data['FactorData.Basic_factor.high_minute']

        dist = 1. - np.nanmax(high.values, axis=0) / close.values[-1]
        ans = pd.Series(dist, index=close.columns)
        ans[~np.isfinite(ans)] = np.nan
        return ans

