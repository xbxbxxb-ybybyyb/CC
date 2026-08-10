import numpy as np
import bottleneck as bn
from future_factor import FutureFactor

class MinuteIndexHLUniqueBuyRetDiff(FutureFactor):
    '''
    Description: high_low_diff(BuyTradeNum/BuyUniqueOrderNum, 20), cs_mean(r(20))
    Class: Group_Stat
    Author: lixr, modified by jinpx
    '''
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'BuyUniqueOrderNum', 'BuyTradeNum', 'adjfactor']
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        close = data['close'].values
        adjfactor = data['adjfactor'].values
        buy_unique_num = data['BuyUniqueOrderNum'].values
        buy_trade_num = data['BuyTradeNum'].values
        close_adj = close * adjfactor
        
        n = 20
        buy_order_size = buy_trade_num[-1,:] / buy_unique_num[-1,:]
        buy_order_size[np.isinf(buy_order_size)] = np.nan
        buy_order_size_rank = (bn.rankdata(buy_order_size)-1)/(len(buy_order_size)-1)
        ret = (close_adj[-1,:] - close_adj[-n,:]) / close_adj[-n,:]
        f = np.nanmean(ret[buy_order_size_rank > 0.75]) - np.nanmean(ret[buy_order_size_rank < 0.25])

        if np.isnan(f):
            f = 0
            
        return f