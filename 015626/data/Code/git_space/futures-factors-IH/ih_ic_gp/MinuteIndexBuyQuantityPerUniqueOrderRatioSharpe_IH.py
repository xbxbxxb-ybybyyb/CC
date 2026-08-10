import numpy as np
from future_factor import FutureFactor

class MinuteIndexBuyQuantityPerUniqueOrderRatioSharpe_IH(FutureFactor):
    '''
    Description: (ts_mean(buy_quantity_per_unique_order_ratio, 5) / ts_std(buy_quantity_unique_order_ratio, 5),
                buy_quantity_per_unique_order_ratio = cs_mean((BuyTradeQuantity / BuyUniqueOrderNum) 
                / ((BuyTradeQuantity + SellTradeQuantity) / (BuyUniqueOrderNum + SellUniqueOrderNum)), w=index_weight) - 1
    Class: Buy_Sell
    Author: hefj, modified by lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight','BuyUniqueOrderNum', 'SellUniqueOrderNum', 'BuyTradeQuantity', 'SellTradeQuantity']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 5
        weight = data['weight'].values
        buy_unique = data['BuyUniqueOrderNum'].values
        buy_q = data['BuyTradeQuantity'].values
        sell_unique = data['SellUniqueOrderNum'].values
        sell_q = data['SellTradeQuantity'].values
        
        buy_q_per_order = buy_q / buy_unique
        q_per_order = (buy_q + sell_q) / (buy_unique + sell_unique)
        f_temp = np.nansum(buy_q_per_order / q_per_order * weight, axis = 1) - 1
        
        return np.nanmean(f_temp[-lb:]) / np.nanstd(f_temp[-lb:])