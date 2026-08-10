import numpy as np
from future_factor import FutureFactor

class MinuteSpreadStdMeanRatio(FutureFactor):
    '''
    Description: BidAskVol / BidAskMean
    Class: 
    Author: jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'main'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC': ['BidAskVol', 'BidAskMean']}
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):

        BidAskVol = data['BidAskVol_cont_IC'].values
        BidAskMean = data['BidAskMean_cont_IC'].values
                
        SpreadStdMeanRatio = BidAskVol / BidAskMean
        
        N = 20
        f = np.nanmean(SpreadStdMeanRatio[-N:])
        
        return f