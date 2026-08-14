from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class HfLast120RangeMeanRatio(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.high_adj_minute", "FactorData.Basic_factor.low_adj_minute"]
    lag = 1

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])        
        high = database.depend_data['FactorData.Basic_factor.high_adj_minute']
        low = database.depend_data['FactorData.Basic_factor.low_adj_minute']

        minute_high = high.values[-240:]
        minute_low = low.values[-240:]
        minute_range = minute_high - minute_low        
        ans = np.nanmean(minute_range[:-120], axis=0) / np.nanmean(minute_range[-120:], axis=0)
        ans = pd.Series(ans, index=high.columns)
        ans[~np.isfinite(ans)] = np.nan
        return ans