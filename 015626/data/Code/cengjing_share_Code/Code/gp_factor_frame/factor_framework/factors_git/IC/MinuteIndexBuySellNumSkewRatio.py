from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class MinuteIndexBuySellNumSkewRatio(FutureFactor):
    '''
    Description: ts_mean(cs_skew(BuyTradeNum) / cs_skew(SellTradeNum), 10)
    Class: Buy_Sell
    Author: lixr, modified by shentq
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeNum', 'SellTradeNum']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n = 10

        buy = data['BuyTradeNum'].values[-n:]
        sell = data['SellTradeNum'].values[-n:]

        buy_skew = stats.skew(buy, axis=1, nan_policy='omit')
        sell_skew = stats.skew(sell, axis=1, nan_policy='omit')

        return np.nanmean(buy_skew / sell_skew)