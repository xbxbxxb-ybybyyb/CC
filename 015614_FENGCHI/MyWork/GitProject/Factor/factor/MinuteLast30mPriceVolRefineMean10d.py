import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class MinuteLast30mPriceVolRefineMean10d(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.amt_minute", "FactorData.Basic_factor.close_minute"]
    lag = 0
    reform_window = 10

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        amt = database.depend_data["FactorData.Basic_factor.amt_minute"]
        close = database.depend_data["FactorData.Basic_factor.close_minute"]
        stk_code = amt.columns
        amt, close = amt.values, close.values
        ret = close[-1] / close[-31] - 1
        ret_rank = pd.Series(ret).rank(pct=True).values
        amt_ret = np.nansum(amt[-120:], axis=0) / np.nansum(amt[-150:-30], axis=0) - 1
        amt_ret_rank = pd.Series(amt_ret).rank(pct=True).values
        result = -(1 + ret_rank) * (1 + amt_ret_rank)
        result = pd.Series(result, index=stk_code)
        return result

    def reform(self, temp_result):
        alpha = temp_result.rolling(self.reform_window, min_periods=1).mean()
        return alpha
