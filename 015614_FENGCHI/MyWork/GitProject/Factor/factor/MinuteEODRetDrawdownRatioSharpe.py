import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class MinuteEODRetDrawdownRatioSharpe(BaseFactor):
    depend_data = ["FactorData.Basic_factor.close_minute"]
    reform_window = 10

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["merge", "merge"])
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        stk_code = close.columns
        close = close.values
        ret = (close - close[0]) / close[0]
        dd = (ret[-1] - ret[-60]) / (ret[-60] - np.nanmin(ret[-60:], axis=0))
        result = pd.Series(-dd, index=stk_code)
        return result

    def reform(self, temp_result):
        alpha = temp_result.rolling(self.reform_window, min_periods=1).mean()\
                / temp_result.rolling(self.reform_window, min_periods=1).std()
        return alpha