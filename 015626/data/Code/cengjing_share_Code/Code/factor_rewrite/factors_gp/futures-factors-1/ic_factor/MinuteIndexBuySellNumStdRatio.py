from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class MinuteIndexBuySellNumStdRatio(FutureFactor):
    '''
    Description: ts_mean(cs_std(BuyTradeNum) / cs_std(SellTradeNum), 5)
    Class: Buy_Sell
    Author: lixr, modified by shentq
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeNum', 'SellTradeNum']
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n = 5

        buy = data['BuyTradeNum'].values[-n:]
        sell = data['SellTradeNum'].values[-n:]

        buy_std = np.nanstd(buy, axis=1)
        sell_std = np.nanstd(sell, axis=1)

        return np.nanmean(buy_std / sell_std)