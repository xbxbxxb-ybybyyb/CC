import numpy as np
import pandas as pd
from future_factor import FutureFactor
from scipy.stats import skew



class  MinuteIndexObVolWeightedRatio_IH(FutureFactor):
    '''
    Description: "(weighted_cs_mean(BidVolMean[-1], w=index_weight) - weighted_cs_mean(AskVolMean[-1], w=index_weight))
                    / (weighted_cs_mean(BidVolMean[-1], w=index_weight) + weighted_cs_mean(AskVolMean[-1], w=index_weight))"
    Class:Bid_Ask
    Author: shentq modeified by liuz
    '''
    data_type = 'IndexStock'
    instrument_type='recent'
    days_past=0
    data_dict=dict()
    data_dict['Stock'] = ['BidVolMean', 'AskVolMean', 'weight']

    normalize_size=20*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        BidVolMean = data['BidVolMean'].values[-1]
        AskVolMean = data['AskVolMean'].values [-1]
        weight = data['weight'].values[-1]
        bid_vol_sum = np.nansum(BidVolMean*weight)
        ask_vol_sum = np.nansum(AskVolMean*weight)
        
        if (bid_vol_sum + ask_vol_sum) == 0:
            factor = 0
        else:
            factor = (bid_vol_sum - ask_vol_sum) / (bid_vol_sum + ask_vol_sum)
        return factor


