import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class MinReturnVolUp2Down5d(BaseFactor):
    depend_data = ['FactorData.Basic_factor.close_minute']
    reform_window = 4

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        stk_code = close.columns
        close = close.values
        ret = close[1:] / close[:-1] - 1
        up = np.nanstd(np.where(ret < 0, np.nan, ret), axis=0)
        down = np.nanstd(np.where(ret > 0, np.nan, ret), axis=0)
        result = -up / down
        result = pd.Series(result, index=stk_code)
        return result

    def reform(self, temp_result):
        alpha = temp_result.rolling(5, 4).mean()
        return alpha
