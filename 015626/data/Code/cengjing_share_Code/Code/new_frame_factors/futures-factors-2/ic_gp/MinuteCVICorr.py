import numpy as np
import pandas as pd
from future_factor import FutureFactor

    
    
class  MinuteCVICorr(FutureFactor):
    '''
    Description: -corr(Index_ClosePx, Interest + Volume, 30)
    Class:PV_Corr
    Author: shentq modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Index_Id'] ={'000905.SH':['close']}
    data_dict['Future_Data'] =['volume', 'interest']
    
    normalize_size=20*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        index_close_list =  data['close_000905.SH'].values 
        volume_list =  data['volume'].values 
        interest_list =  data['interest'].values 
        
        new_volume_list = [volume_list[i]+interest_list[i] for i in range(len(volume_list))]
        factor = -np.corrcoef(index_close_list[-30:],new_volume_list[-30:])[0,1]
        
        return factor
    
    
