import numpy as np
from future_factor import FutureFactor

class MinuteIndexVOIMean(FutureFactor):
    '''
    Description: ts_mean((cs_sum(where(close > delay(close, 1), BuyTradeMoney, 0)) - cs_sum(where(close < delay(close, 1), SellTradeMoney, 0)))
                / (cs_sum(where(close > delay(close, 1), BuyTradeMoney, 0)) + cs_sum(where(close < delay(close, 1), SellTradeMoney, 0))), 60)
    Class: Buy_Sell
    Author: hefj, modified by lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor', 'close', 'BuyTradeMoney', 'SellTradeMoney']
    normalize_size = 15 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 60
        adjfactor = data['adjfactor'].values
        close = data['close'].values * adjfactor
        close[close == 0] = np.nan
        buy = data['BuyTradeMoney'].values
        sell = data['SellTradeMoney'].values
        
        buy_up = np.nansum(np.where(close[-lb:] > close[-lb - 1: -1], buy[-lb:], np.nan), axis=1)
        sell_down = np.nansum(np.where(close[-lb:] < close[-lb - 1: -1], sell[-lb:], np.nan), axis=1)
        ratio = (buy_up - sell_down) / (buy_up + sell_down)
        
        return ratio.mean()