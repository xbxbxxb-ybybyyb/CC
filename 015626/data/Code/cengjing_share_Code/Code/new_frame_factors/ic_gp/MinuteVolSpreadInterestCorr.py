import numpy as np
import pandas as pd
from future_factor import FutureFactor
from scipy.stats import skew



class  MinuteVolSpreadInterestCorr(FutureFactor):
    '''
    Description: 
    Class:Liquidity
    Author: lixr modeified by liuz
    '''
    data_type='Future'
    instrument_type='main'
    days_past=1
    data_dict=dict()
    data_dict['Future_Data'] = ['AskVol', 'BidVol','interest']

    normalize_size=20*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        AskVol = data['AskVol'].values 
        BidVol = data['BidVol'].values 
        Interest = data['interest'].values 

        vol_spread = BidVol-AskVol
        factor = -np.corrcoef(vol_spread[-120:], Interest[-120:])[0,1]
        return  factor
    