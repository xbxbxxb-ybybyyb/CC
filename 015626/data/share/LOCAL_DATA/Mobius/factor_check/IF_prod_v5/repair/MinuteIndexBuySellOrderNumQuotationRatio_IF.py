import numpy as np
from future_factor import FutureFactor

class MinuteIndexBuySellOrderNumQuotationRatio_IF(FutureFactor):
    '''
    Description: 
    Class: 
    Author: jinpx 
    '''    
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['Buy1NumOrdersMean', 'Sell1NumOrdersMean', 'BuyNumOrdersSumMean', 'SellNumOrdersSumMean']
    normalize_size = 800
    normalize_type = 'ts_rank'

    def calculate(self, data):
        
        Buy1NumOrdersMean = data['Buy1NumOrdersMean'].values
        Sell1NumOrdersMean = data['Sell1NumOrdersMean'].values
        BuyNumOrdersSumMean = data['BuyNumOrdersSumMean'].values
        SellNumOrdersSumMean = data['SellNumOrdersSumMean'].values
        Buy1NumOrdersMean[Buy1NumOrdersMean==0] = np.nan
        Sell1NumOrdersMean[Sell1NumOrdersMean==0] = np.nan
        
        buy_ratio = BuyNumOrdersSumMean / Buy1NumOrdersMean
        sell_ratio = SellNumOrdersSumMean / Sell1NumOrdersMean
        
        N = 10
        f = - (np.nanmean(buy_ratio[-N:]) - np.nanmean(sell_ratio[-N:]))
        
        return f