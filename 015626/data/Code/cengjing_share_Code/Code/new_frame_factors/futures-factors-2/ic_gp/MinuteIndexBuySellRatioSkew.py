import numpy as np
from scipy.stats import skew
from future_factor import FutureFactor

class MinuteIndexBuySellRatioSkew(FutureFactor):
    '''
    Description: -ts_skew(cs_mean(BuyTradeQuantity / SellTradeQuantity - 1), 60)
    Class: Buy_Sell
    Author: hefj, modified by jinpx
    '''
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeQuantity', 'SellTradeQuantity']
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        buytradequantity = data['BuyTradeQuantity'].values
        selltradequantity = data['SellTradeQuantity'].values

        N = 60
        buy_sell_trade_quantity_ratio = buytradequantity[-N:] / selltradequantity[-N:]
        buy_sell_trade_quantity_ratio[np.isinf(buy_sell_trade_quantity_ratio)] = np.nan
        buy_sell_trade_quantity_ratio_mean = np.nanmean(buy_sell_trade_quantity_ratio, axis=1)
        f = - skew(buy_sell_trade_quantity_ratio_mean, nan_policy='omit')
        if np.isnan(f) or np.isinf(f):
            f = 0
            
        return f