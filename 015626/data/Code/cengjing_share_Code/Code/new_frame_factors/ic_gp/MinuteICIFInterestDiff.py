import numpy as np
from future_factor import FutureFactor

class MinuteICIFInterestDiff(FutureFactor):
    '''
    Description: mean(interest_IF, 60) - mean(interest_IC, 60)
    Class: Multi-Variety
    Author: lixr
    '''
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Other_Variety'] = {'IC':['interest'],'IF':['interest']}
    normalize_size = 20 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        n = 60
        interest1 = data['interest_IC'].values[-n:]
        interest2 = data['interest_IF'].values[-n:]
        
        factor_value = np.nanmean(interest2) - np.nanmean(interest1) 
        
        return factor_value