import numpy as np
from future_factor import FutureFactor

class MinuteIndexBuySellRatioCloseCorrSharpe(FutureFactor):
    '''
    Description: weighted_cs_mean(ts_corr(close, ((BuyTradeQuantitiy - SellTradeQuantity) / (BuyTradeQuantity + SellTradeQuantity)), 50), w=index_weight)
                / weighted_cs_std(ts_corr(close, ((BuyTradeQuantity - SellTradeQuantity) / (BuyTradeQuantity + SellTradeQuantity)), 50), w=index_weight)
    Class: Buy_Sell
    Author: hefj, modified by lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight','SellTradeQuantity', 'BuyTradeQuantity', 'close', 'adjfactor']
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        def corr_coef(x, y):
            mask = np.isnan(x) | np.isnan(y) | np.isinf(x) | np.isinf(y)
            x = np.where(mask, np.nan, x)
            y = np.where(mask, np.nan, y)
            return np.nanmean((x - np.nanmean(x, axis=0)) * (y - np.nanmean(y, axis=0)), axis=0) / (np.nanstd(x, axis=0) * np.nanstd(y, axis=0))

        lb = 50
        weight = data['weight'].values
        adjfactor = data['adjfactor'].values
        close = data['close'].values * adjfactor
        close[close == 0] = np.nan
        buy = data['BuyTradeQuantity'].values
        sell = data['SellTradeQuantity'].values
        
        ratio = (buy[-lb:] - sell[-lb:]) / (buy[-lb:] + sell[-lb:])
        close = close[-lb:]
        corr = corr_coef(close, ratio)
        corr[np.isinf(corr)] = np.nan
        mean = np.nansum(corr * weight[-1])
        std = np.nansum(((corr - mean) ** 2) * weight[-1]) ** 0.5
        
        return -mean / std