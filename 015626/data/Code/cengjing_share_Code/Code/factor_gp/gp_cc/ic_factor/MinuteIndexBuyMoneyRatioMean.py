from future_factor import FutureFactor
import numpy as np


class MinuteIndexBuyMoneyRatioMean(FutureFactor):
    data_type = 'IndexStock'
    days_past = 7
    data_dict = {}
    data_dict['Stock'] = ['BuyTradeMoney']
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 20
        buy_money = data['BuyTradeMoney'].values[-6 * 237:]
        buy_money[buy_money == 0] = np.nan
        nan_num = np.isnan(buy_money).sum(axis=0)
        buy_money = buy_money[:, nan_num == 0]
        buy_money = buy_money.reshape(6, 237, -1)
        buy_ratio = buy_money[-1] / np.nanmean(buy_money[:-1], axis=0)
        f = np.nanmean(buy_ratio[-lb:])
        return f
