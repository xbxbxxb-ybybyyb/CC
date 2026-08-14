import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor


class MeanTurn2RetDown5d(BaseFactor):
    depend_data = ['FactorData.Basic_factor.turn', 'FactorData.Basic_factor.close',
                   'FactorData.Basic_factor.open']
    reform_window = 5

    def calc_single(self, database):
        turn = database.depend_data['FactorData.Basic_factor.turn']
        op = database.depend_data['FactorData.Basic_factor.open']
        close = database.depend_data['FactorData.Basic_factor.close']
        stk_code = turn.columns
        turn, op, close = turn.values[-1], op.values[-1], close.values[-1]
        ret = close / op - 1
        result = turn / np.abs(ret)
        result[close >= op] = np.nan
        result = pd.Series(-result, index=stk_code)
        return result

    def reform(self, temp_result):
        alpha = temp_result.rolling(5, 1).mean()
        return alpha
