import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class MinuteReturnSkew(BaseFactor):
    depend_data = ['FactorData.Basic_factor.close_minute']

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        stk_code = close.columns
        close = close.resample('5T').last()
        skew = close.pct_change().iloc[-30:].skew().values
        if len(skew[~np.isnan(skew)]) == 0:
            skew = np.nan * np.ones(len(skew))
        result = pd.Series(-skew, index=stk_code)
        return result
