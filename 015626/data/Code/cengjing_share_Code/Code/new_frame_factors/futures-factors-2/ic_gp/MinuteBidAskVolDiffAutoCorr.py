import numpy as np
from future_factor import FutureFactor

class MinuteBidAskVolDiffAutoCorr(FutureFactor):
    '''
    Description: autocorr(BidVol - AskVol, 50)
    Class: Bid_Ask
    Author: lixr, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Future_Data'] = ['BidVol','AskVol']
    normalize_size = 10 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        n = 50        
        askvol_list = data['AskVol'].values[-n:]
        bidvol_list = data['BidVol'].values[-n:]    
        mask = np.isnan(askvol_list) | np.isnan(bidvol_list)
        askvol_list = askvol_list[~mask]
        bidvol_list = bidvol_list[~mask]
        
        bidaskvol_diff = bidvol_list - askvol_list   
        factor_value = np.corrcoef(bidaskvol_diff[:-1], bidaskvol_diff[1:])[0,1]
        
        if np.isnan(factor_value) or np.isinf(factor_value):
            return 0
        else:
            return factor_value