import numpy as np
from future_factor import FutureFactor

class MinuteInterestTreasure120Corr(FutureFactor):
    '''
    Description: corr(Interest, Treasure_LastPx, 120)
    Class: Treasure_Future
    Author: shentq, modified by jinpx
    '''
    data_type = 'Future'
    instrument_type = 'main'
    days_past = 1
    data_dict = dict()
    data_dict['Future_Data'] = ['interest']
    data_dict['Other_Variety'] = {'T':['close']}
    normalize_size = 20 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
                
        interest = data['interest'].values
        close_T = data['close_T'].values
        
        f = np.corrcoef(interest[-120:], close_T[-120:])[0, 1]
        
        return f