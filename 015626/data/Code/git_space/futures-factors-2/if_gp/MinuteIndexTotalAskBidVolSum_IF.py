import numpy as np
from future_factor import FutureFactor
from operators_cc import *

class MinuteIndexTotalAskBidVolSum_IF(FutureFactor):
    '''
    Description: TotalAskVol / (Mean of TotalAskVol during past 5 days at the same minute) + TotalBidVol / (Mean of TotalBidVol during past 5 days at the same minute)
    Class: 
    Author: jinpx
    '''    
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['TotalAskVol', 'TotalBidVol']
    normalize_size = 60 
    normalize_type = 'ts_rank'

    def calculate(self, data):
        
        TotalAskVol = data['TotalAskVol'].values
        TotalBidVol = data['TotalBidVol'].values
        
        TotalAskVol_ratio = TotalAskVol[-237:] / r(np.nanmean(TotalAskVol[-1422:-237].reshape(5, 237, len(TotalAskVol[0])), axis=0))
        TotalBidVol_ratio = TotalBidVol[-237:] / r(np.nanmean(TotalBidVol[-1422:-237].reshape(5, 237, len(TotalBidVol[0])), axis=0))
        
        f = np.nansum(TotalAskVol_ratio[-1]) + np.nansum(TotalBidVol_ratio[-1])
        
        return f