import numpy as np
from future_factor import FutureFactor

class MinuteBidAskVolRatio(FutureFactor):
    '''
    Description: mean(bidvao_ratio + askvol_ratio, 60), where
                bidvol_ratio = bidvol / (the average bidvol at current time over past 5 trading days)
                askvol_ratio = askvol / (the average askvol at current time over past 5 trading days)
    Class: 
    Author: lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC': ['BidVol','AskVol']}
    normalize_size = 3 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        n = 60
        bidvol_list = data['BidVol_cont_IC'].values
        askvol_list = data['AskVol_cont_IC'].values
        
        bidvol_ratio = (bidvol_list[-240:] / np.nanmean(bidvol_list[-240*6:-240].reshape(5, 240), axis = 0))[-n:]
        askvol_ratio = (askvol_list[-240:] / np.nanmean(askvol_list[-240*6:-240].reshape(5, 240), axis = 0))[-n:]
        factor_value = np.nanmean(bidvol_ratio + askvol_ratio)
        
        return factor_value