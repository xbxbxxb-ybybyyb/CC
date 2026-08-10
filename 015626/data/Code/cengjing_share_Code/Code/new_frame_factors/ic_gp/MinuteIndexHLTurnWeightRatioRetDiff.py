from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor
import bottleneck as bn


class MinuteIndexHLTurnWeightRatioRetDiff(FutureFactor):
    '''
    Description:
    Class: Group_Stat
    Author: lixr, modified by shentq
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'amount', 'weight']
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n1 = 10
        n2 = 60

        close = data['close'].values[-(n1 + 1):]
        rtn = close[-1] / close[-(n1 + 1)] - 1

        weight = data['weight'].values[-n2:]
        turnover = data['amount'].values[-n2:]

        turnover_weight_ratio = turnover / weight
        turnover_weight_ratio = np.where(np.isinf(turnover_weight_ratio), np.nan, turnover_weight_ratio)

        turnover_weight_ratio_rank = self.rank(np.nanmean(turnover_weight_ratio, axis=0), ascending=True, pct=True)

        factor_value = np.nansum(rtn[turnover_weight_ratio_rank > 0.9]) - np.nansum(
            rtn[turnover_weight_ratio_rank < 0.1])

        if np.isnan(factor_value) or np.isinf(factor_value):
            factor_value = 0

        return factor_value

    def rank(self, arr, axis=0, ascending=True, pct=False):
        sign = 1.0 if ascending else -1.0
        rank_value = bn.rankdata(sign * arr, axis=axis) + 1
        if pct:
            rank_value = rank_value / arr.shape[axis]

        return rank_value