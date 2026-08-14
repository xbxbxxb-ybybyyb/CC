import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class HighLowStdRatio_mean20d(BaseFactor):
    depend_data = ['FactorData.Basic_factor.high_minute', 'FactorData.Basic_factor.low_minute']
    reform_window = 20

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        high = database.depend_data['FactorData.Basic_factor.high_minute']
        low = database.depend_data['FactorData.Basic_factor.low_minute']
        stk_code = high.columns
        high = high.iloc[-210:].rolling(10).max().rolling(120).std()
        low = low.iloc[-210:].rolling(10).min().rolling(120).std()
        result = -np.nanmean(high.values / low.values, axis=0)
        result = pd.Series(result, index=stk_code)
        return result

    def reform(self, temp_result):
        alpha = temp_result.rolling(20).mean()
        return alpha
