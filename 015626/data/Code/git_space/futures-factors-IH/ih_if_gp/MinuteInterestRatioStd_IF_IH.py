import numpy as np
from future_factor import FutureFactor

class MinuteInterestRatioStd_IF_IH(FutureFactor):
    '''
    Description: 
    Class: 
    Author: jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IH':['interest']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'

    def calculate(self, data):
        
        interest = data['interest_cont_IH'].values
        
        N = 20
        interest_ratio = interest[-N:] / np.nansum(interest[-N:]) 

        f = - np.nanstd(interest_ratio[-N:])
        
        return f