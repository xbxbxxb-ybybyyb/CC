import numpy as np
from future_factor import FutureFactor

class MinuteIndexBuyOrderNumQuotationRatio_IF(FutureFactor):
    '''
    Description: 
    Class: 
    Author: jinpx 
    '''    
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['Buy1NumOrdersMean', 'BuyNumOrdersSumMean']
    normalize_size = 500
    normalize_type = 'ts_rank'

    def calculate(self, data):
        
        Buy1NumOrdersMean = data['Buy1NumOrdersMean'].values
        BuyNumOrdersSumMean = data['BuyNumOrdersSumMean'].values

        Buy1NumOrdersMean[Buy1NumOrdersMean==0] = np.nan
        
        buy_ratio = BuyNumOrdersSumMean / Buy1NumOrdersMean
        
        N = 10        
        f = - np.nanmean(buy_ratio[-N:])
        
        return f