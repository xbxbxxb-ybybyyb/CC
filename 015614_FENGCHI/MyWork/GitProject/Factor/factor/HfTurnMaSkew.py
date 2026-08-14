from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class HfTurnMaSkew(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.amt_minute"]
    lag = 1

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])        
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']

        minute_amt = amt.iloc[-240:]
        minute_amt_ma= minute_amt.rolling(window=5,min_periods=1).mean()        
        ans = - minute_amt_ma.skew()
        ans[~np.isfinite(ans)] = np.nan
        return ans