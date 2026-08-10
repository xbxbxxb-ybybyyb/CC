import numpy as np
from future_factor import FutureFactor

class MinuteInterestTreasure120Corr_IH(FutureFactor):
    '''
    Description: corr(Interest, Treasure_LastPx, 120)
    Class: Treasure_Future
    Author: shentq, modified by jinpx
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IH': ['interest']}
    data_dict['Other_Variety'] = {'T':['close']}
    normalize_size = 20 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
                
        interest = data['interest_cont_IH'].values
        close_T = data['close_T'].values
        
        f = np.corrcoef(interest[-120:], close_T[-120:])[0, 1]
        
        return f