from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor
import bottleneck as bn


class MinuteIndexHLTurnoverUniqueBuyRatioDiff_IH(FutureFactor):
    '''
    Description: cs_mean(where(turnoverrank > 0.5, buyuniqueratio, nan)) - cs_mean(where(turnoverrank < 0.5, buyuniqueratio, nan)),
                 turnoverrank = cs_rank(ts_mean(Turnover, 120)),buyuniqueratio = -ts_mean(BuyUniqueOrderNum / BuyTradeNum, 10)
    Class: Group_Stat
    Author: lixr, modified by shentq
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'BuyTradeNum', 'amount']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n1 = 10
        n2 = 120

        buy_unique_num = data['BuyUniqueOrderNum'].values[-n1:]
        buy_trade_num = data['BuyTradeNum'].values[-n1:]

        buy_unique_ratio = -buy_unique_num / buy_trade_num
        buy_unique_ratio[np.isinf(buy_unique_ratio)] = np.nan

        ratio_mean = np.nanmean(buy_unique_ratio, axis=0)

        turnover = data['amount'].values[-n2:]
        turnover_rank = self.rank(np.nanmean(turnover, axis=0), ascending=True, pct=True)

        factor_value = np.nanmean(ratio_mean[turnover_rank > 0.5]) - np.nanmean(ratio_mean[turnover_rank < 0.5])

        if np.isnan(factor_value) or np.isinf(factor_value):
            factor_value = 0

        return factor_value

    def rank(self, arr, axis=0, ascending=True, pct=False):
        sign = 1.0 if ascending else -1.0
        rank_value = bn.rankdata(sign * arr, axis=axis) + 1
        if pct:
            rank_value = rank_value / arr.shape[axis]

        return rank_value