import numpy as np
import bottleneck as bn
from future_factor import FutureFactor

class MinuteIndexHighLowBuySellMoneyPerUniqueSumReturnDiff_IH(FutureFactor):
    '''
    Description: 
    Class: 
    Author: jinpx
    '''    
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'SellUniqueOrderNum', 'BuyTradeMoney', 'SellTradeMoney', 'close', 'adjfactor']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):

        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values
        BuyTradeMoney = data['BuyTradeMoney'].values
        SellTradeMoney = data['SellTradeMoney'].values
        close = data['close'].values
        adjfactor = data['adjfactor'].values
        close_adj = close * adjfactor
        r = np.diff(close_adj, axis=0) / close_adj[:-1]
        
        BuyMoneyPerUnique = BuyTradeMoney / BuyUniqueOrderNum
        SellMoneyPerUnique = SellTradeMoney / SellUniqueOrderNum
        BuySellMoneyPerUniqueSum = BuyMoneyPerUnique + SellMoneyPerUnique

        N = 40
        BuySellMoneyPerUniqueSum_mean = np.nanmean(BuySellMoneyPerUniqueSum[-N:], axis=0)
        BuySellMoneyPerUniqueSum_mean[np.isnan(BuySellMoneyPerUniqueSum_mean)] = np.nanmean(BuySellMoneyPerUniqueSum_mean)
        BuySellMoneyPerUniqueSum_mean_rank = (bn.rankdata(BuySellMoneyPerUniqueSum_mean)-1)/(len(BuySellMoneyPerUniqueSum_mean)-1)
        r_sum = np.nansum(r[-N:], axis=0)
        f = np.nanmean(r_sum[BuySellMoneyPerUniqueSum_mean_rank>0.5]) - np.nanmean(r_sum[BuySellMoneyPerUniqueSum_mean_rank<0.5])
        
        return f