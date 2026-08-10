import numpy as np
from future_factor import FutureFactor

class MinuteSpreadStdMeanRatio_IF_IH(FutureFactor):
    '''
    Description: BidAskVol / BidAskMean
    Class: 
    Author: jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IH':['BidAskVol', 'BidAskMean']}
    normalize_size = 120
    normalize_type = 'ts_rank'

    def calculate(self, data):

        BidAskVol = data['BidAskVol_cont_IH'].values
        BidAskMean = data['BidAskMean_cont_IH'].values
        
        SpreadStdMeanRatio = BidAskVol / BidAskMean
        
        N = 20
        f = np.nanmean(SpreadStdMeanRatio[-N:])
        
        return f