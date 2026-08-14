import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor


class AmtRet20d(BaseFactor):
    depend_data = ["FactorData.Basic_factor.close", "FactorData.Basic_factor.amt", "FactorData.Basic_factor.adjfactor"]
    lag = 20
    reform_window = 20

    def calc_single(self, database):
        close = database.depend_data["FactorData.Basic_factor.close"]
        amt = database.depend_data["FactorData.Basic_factor.amt"]
        adjfactor = database.depend_data["FactorData.Basic_factor.adjfactor"]
        stk_code = close.columns
        close, amt, adjfactor = close.values, amt.values, adjfactor.values
        close = close * adjfactor / adjfactor[-1]
        rtn = close[-1] / close[-self.lag - 1] - 1
        rtn_sign = np.where(rtn >= 0, 1, -1)
        result = pd.Series(-np.log(amt[-1] / amt[-self.lag - 1]) * rtn_sign, index=stk_code)
        return result

    def reform(self, temp_result):
        alpha = temp_result.rolling(self.reform_window).sum()
        return alpha
