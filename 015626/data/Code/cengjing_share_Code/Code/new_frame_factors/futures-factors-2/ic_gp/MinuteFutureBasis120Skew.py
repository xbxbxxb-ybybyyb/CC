import numpy as np
import pandas as pd
from future_factor import FutureFactor
from scipy.stats import skew

class  MinuteFutureBasis120Skew(FutureFactor):
    '''
    Description: -skew(ClosePx - Index_ClosePx, 120)
    Class:Future_Spot_Price
    Author: shentq modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()

    data_dict['Future_Data'] = ['close']
    data_dict['Index_Id'] = {'000905.SH':['close',]}

    
    normalize_size=20*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        index_close_list = data['close_000905.SH'].values
        close_list = data['close'].values
        future_basis_list = close_list-index_close_list
        
        factor = -skew(future_basis_list[-120:])
        return factor
    