from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class MinuteIndexHLTurnoverBuySellNumRatioDiff(FutureFactor):
    '''
    Description: cs_mean(where(turnoverrank > 0.5, buysellratio, nan)) - cs_mean(where(turnoverrank < 0.2, buysellratio, nan)),
                 turnoverrank = cs_rank(ts_mean(Turnover, 140)),buysellratio = ts_mean(BuyTradeNum / SellTradeNum, 6)
    Class: Group_Stat
    Author: lixr, modified by shentq
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeNum', 'SellTradeNum', 'amount']
    normalize_size = 20 * 240
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n1 = 6
        n2 = 140

        buy = data['BuyTradeNum'].values[-n1:]
        sell = data['SellTradeNum'].values[-n1:]
        ratio = buy / sell
        ratio[np.isinf(ratio)] = np.nan
        ratio_mean = np.nanmean(ratio, axis=0)

        turnover = data['amount'].values[-n2:]
        turnover_rank = self.rank(np.nanmean(turnover, axis=0), ascending=True, pct=True)

        return np.nanmean(ratio_mean[turnover_rank > 0.5]) - np.nanmean(ratio_mean[turnover_rank < 0.5])

    def rank(self, arr, axis=0, ascending=True, pct=False):
        sign = 1.0 if ascending else -1.0
        rank_value = (sign * arr).argsort(axis=axis).argsort(axis=axis) + 1
        if pct:
            rank_value = rank_value / arr.shape[axis]

        return rank_value