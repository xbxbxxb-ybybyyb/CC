from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class MinuteIndexHLWeightDivergence(FutureFactor):
    '''
    Description:
    Class: Group_Stat
    Author: lixr, modified by shentq
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'weight']
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n = 30
        threshold = 0.2

        close = data['close'].values[-(n + 1):]
        rtn = close[-1] / close[-(n + 1)] - 1

        weight = data['weight'].values[-1]
        weight_rank = self.rank(weight, ascending=True, pct=True)

        std_1 = np.nanstd(rtn[weight_rank < threshold])
        std_2 = np.nanstd(rtn[weight_rank > (1 - threshold)])

        factor_value = std_1 / std_2

        if np.isnan(factor_value) or np.isinf(factor_value):
            factor_value = 0

        return factor_value

    def rank(self, arr, axis=0, ascending=True, pct=False):
        sign = 1.0 if ascending else -1.0
        rank_value = (sign * arr).argsort(axis=axis).argsort(axis=axis) + 1
        if pct:
            rank_value = rank_value / arr.shape[axis]

        return rank_value