import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class MinuteALTKurt(BaseFactor):
    depend_data = ["FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.amt_minute"]
    reform_window = 9

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        stk_code = close.columns
        ret = close.pct_change()
        amt_ewm = amt.ewm(span=10).mean()
        long_amt = pd.DataFrame(np.where(ret.values > 0, amt_ewm.values, np.nan))
        result = pd.Series(-1 * long_amt.kurt().values, index=stk_code)
        return result

    def reform(self, temp_result):
        alpha = temp_result.rolling(10, min_periods=1).mean()
        return alpha
