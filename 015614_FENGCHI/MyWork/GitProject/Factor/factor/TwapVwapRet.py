import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor


class TwapVwapRet(BaseFactor):
    depend_data = ['FactorData.Basic_factor.amt', 'FactorData.Basic_factor.volume',
                   'FactorData.Basic_factor.adjfactor']
    lag = 9
    reform_window = 10

    def calc_single(self, database):
        amt = database.depend_data['FactorData.Basic_factor.amt']
        vol = database.depend_data['FactorData.Basic_factor.volume']
        adj = database.depend_data['FactorData.Basic_factor.adjfactor']
        stk_code = amt.columns
        amt, vol, adj = amt.values * 1000, vol.values * 100, adj.values
        adj = adj / adj[-1]
        vol = vol / adj
        vwap = np.nancumsum(amt, axis=0) / np.nancumsum(vol, axis=0)
        p = amt / vol
        twap = np.nancumsum(p, axis=0) / np.arange(1, len(p) + 1).reshape(len(p), 1)
        r = twap / vwap - 1
        a = np.e ** (np.arange(len(r) - 1, -1, -1) * np.log(0.5) / 5)
        a = a / a.sum()
        res = pd.Series(np.nansum(r * a.reshape(len(r), 1), axis=0), index=stk_code)
        return res

    def reform(self, temp_result):
        alpha = temp_result.rolling(10).mean()
        return alpha
