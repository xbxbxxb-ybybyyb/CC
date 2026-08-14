import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class ClosePercentRank5d(BaseFactor):
    depend_data = ["FactorData.Basic_factor.close_minute"]
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=['drop', 'merge'])
        close_minute = database.depend_data['FactorData.Basic_factor.close_minute']
        stk_code = close_minute.columns
        close_minute = close_minute.values
        result = np.nan * np.ones(close_minute.shape[1])
        for i in range(close_minute.shape[1]):
            mylist = close_minute[:, i]
            if (~np.isnan(mylist[-1])) & ((~np.isnan(mylist)).sum() >= 200):
                ind = np.where(~np.isnan(mylist))[0]
                sort = np.sort(mylist[ind])
                if mylist[-1] < sort[0]:
                    result[i] = (mylist[-1] - sort[0]) / abs(sort[0])
                elif mylist[-1] >= sort[-1]:
                    result[i] = 1 + (mylist[-1] - sort[-1]) / abs(sort[-1])
                else:
                    bigger_this_data = np.where(sort >= mylist[-1])[0]
                    result[i] = bigger_this_data[0] / (len(sort) + 1)
        result = pd.Series(result, index=stk_code).convert_objects(convert_numeric=True)
        return result

    def reform(self, temp_result):
        alpha = -temp_result.rank(axis=1).rolling(self.reform_window, min_periods=int(0.8*self.reform_window)).mean()
        return alpha
