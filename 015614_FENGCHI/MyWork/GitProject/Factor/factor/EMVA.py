import pandas as pd
import numpy as np
from xfactor.BaseFactor import BaseFactor


class EMVA(BaseFactor):
    depend_data = ["FactorData.Basic_factor.high", "FactorData.Basic_factor.low", "FactorData.Basic_factor.amt",
                   "FactorData.Basic_factor.adjfactor", "FactorData.Basic_factor.is_valid_raw"]
    lag = 20
    reform_window = 20

    def calc_single(self, database):
        high = database.depend_data['FactorData.Basic_factor.high']
        low = database.depend_data['FactorData.Basic_factor.low']
        amt = database.depend_data['FactorData.Basic_factor.amt']
        adjfactor = database.depend_data['FactorData.Basic_factor.adjfactor']
        valid = database.depend_data['FactorData.Basic_factor.is_valid_raw']
        stk_code = high.columns
        high, low, amt, adjfactor, valid = high.values, low.values, amt.values, adjfactor.values, valid.values
        high = high * adjfactor / adjfactor[-1]
        low = low * adjfactor / adjfactor[-1]
        high, low, amt = np.where(valid == 1, high, np.nan), np.where(valid == 1, low, np.nan), np.where(
            valid, amt, np.nan)
        hp_0, hp_1 = high[-1] / np.nanmean(high[-self.lag:], axis=0), high[-2] / np.nanmean(high[-self.lag-1:-1],
                                                                                            axis=0)
        lp_0, lp_1 = low[-1] / np.nanmean(low[-self.lag:], axis=0), low[-2] / np.nanmean(low[-self.lag-1:-1], axis=0)
        amt_0 = amt[-1] / np.nanmean(amt[-self.lag:], axis=0)
        a = (hp_0 + lp_0) / 2
        b = (hp_1 + lp_1) / 2
        c = hp_0 - lp_0
        emva = pd.Series((a - b) * c * amt_0, index=stk_code)
        return emva

    def reform(self, temp_result):
        alpha = -temp_result.rolling(self.reform_window).mean()
        return alpha
