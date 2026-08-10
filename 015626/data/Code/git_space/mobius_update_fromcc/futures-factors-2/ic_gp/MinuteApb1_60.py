import numpy as np
from future_factor import FutureFactor

class MinuteApb1_60(FutureFactor):
    '''
    Description: mean(amount / volume, 60) / (sum(amount, 60) / sum(volume, 60))
    Class: PV_Corr
    Author: liuz, modified by jinpx
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC': ['volume', 'amount']}
    normalize_size = 20 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
                
        volume = data['volume_cont_IC'].values
        amount = data['amount_cont_IC'].values
        vwap = amount / volume
        f = np.nanmean(vwap[-60:]) / (np.nansum(amount[-60:]) / np.nansum(volume[-60:]))
        
        return f