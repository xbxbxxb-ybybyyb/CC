from xfactor.BaseFactor import BaseFactor
import pandas as pd
import numpy as np


class MomW(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_badj", "FactorData.Basic_factor.amt",
                   "FactorData.Basic_factor.dealnum"]
    lag = 10
    reform_window = 20
    def calc_single(self, database):
        close_adj = database.depend_data['FactorData.Basic_factor.close_badj']
        amt = database.depend_data['FactorData.Basic_factor.amt']
        dealnum = database.depend_data['FactorData.Basic_factor.dealnum']

        ret = close_adj.values[1:] / close_adj.values[:-1] - 1.
        ret[np.isinf(ret)] = np.nan
        amt_per_deal = amt.values[1:] / dealnum.values[1:]
        amt_per_deal[np.isinf(amt_per_deal)] = np.nan
        higher = amt_per_deal >= np.nanquantile(amt_per_deal, 0.5, axis=0)

        M_high = np.nanprod(np.where(higher, ret, np.nan) + 1., axis=0) - 1.
        M_low = np.nanprod(np.where(~higher, ret, np.nan) + 1., axis=0) - 1.
        ans = M_low - M_high

        ans = pd.Series(ans, index=close_adj.columns)
        ans[~np.isfinite(ans)] = np.nan
        return ans.rank(pct=True)
    def weight(self,series):
        n = len(series)
        w = np.arange(1, (n + 1), 1) / n
        temp = (series * w).sum()
        return temp
    def reform(self, temp_result):
        return temp_result.rolling(20,5).apply(self.weight)
