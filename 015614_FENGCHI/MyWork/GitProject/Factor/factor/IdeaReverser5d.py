from xfactor.BaseFactor import BaseFactor
import pandas as pd
import numpy as np

class IdeaReverser5d(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_badj", "FactorData.Basic_factor.amt", "FactorData.Basic_factor.dealnum", 
                   "FactorData.Basic_factor.is_valid",]
    lag = 10
    reform_window = 5

    def calc_single(self, database):
        close_adj = database.depend_data['FactorData.Basic_factor.close_badj']
        amt = database.depend_data['FactorData.Basic_factor.amt']
        dealnum = database.depend_data['FactorData.Basic_factor.dealnum']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']

        ret = close_adj.values[1:] / close_adj.values[:-1] - 1.
        amt_per_deal = amt.values[1:] / dealnum.values[1:]
        amt_per_deal[np.isinf(amt_per_deal)] = np.nan
        higher = amt_per_deal >= np.nanquantile(amt_per_deal, 0.5, axis=0)
        M_high = np.nansum( np.where(higher, ret, np.nan), axis=0) 
        M_low = np.nansum( np.where(~higher, ret, np.nan), axis=0) 
        ans = M_low - M_high
        ans = pd.Series(ans, index=close_adj.columns)
        ans[is_valid.iloc[-1]==0] = np.nan
        ans[~np.isfinite(ans)] = np.nan
        return ans

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean()
    
            