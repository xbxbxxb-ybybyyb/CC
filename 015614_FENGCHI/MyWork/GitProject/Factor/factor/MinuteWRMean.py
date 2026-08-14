import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class MinuteWRMean(BaseFactor):
    depend_data = ['FactorData.Basic_factor.high_minute', 'FactorData.Basic_factor.low_minute',
                   'FactorData.Basic_factor.close_minute']
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        high = database.depend_data['FactorData.Basic_factor.high_minute']
        low = database.depend_data['FactorData.Basic_factor.low_minute']
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        stk_code = high.columns
        high = np.nanmax(high.values[-10:], axis=0)
        low = np.nanmin(low.values[-10:], axis=0)
        close = close.values[-1]
        wr = (high - close) / (high - low)
        wr[np.isinf(wr)] = 0
        wr = pd.Series(wr, index=stk_code)
        return wr

    def reform(self, temp_result):
        alpha = temp_result.rolling(5).mean()
        return alpha

