from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class MinuteTSD(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.amt_minute"]

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])        
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        
        amt_value = np.where(amt.values==0., np.nan, amt.values)
        tr = amt_value[1:] / amt_value[:-1] - 1.
        tr[np.isinf(tr)] = np.nan
        c = close.values
        ans = - (np.nanmean(tr[-30:], axis=0) / np.nanstd(tr[-30:], axis=0, ddof=1)) * np.sign(c[-1] / c[-31] - 1.)
        ans = pd.Series(ans, index=close.columns)
        ans[~np.isfinite(ans)] = np.nan
        return ans

