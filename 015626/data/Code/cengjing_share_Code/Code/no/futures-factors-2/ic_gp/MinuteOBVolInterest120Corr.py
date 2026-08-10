import numpy as np
import pandas as pd
from future_factor import FutureFactor
from scipy.stats import skew





class  MinuteOBVolInterest120Corr(FutureFactor):
    '''
    Description: corr(Interest, AskVol + BidVol, 120)
    Class: Bid_Ask
    Author:  shentq modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Continuous_Data'] = {'IC':['AskVol', 'BidVol','interest']}

    normalize_size=20*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        AskVol = data['AskVol_cont_IC'].values 
        BidVol = data['BidVol_cont_IC'].values 
        Interest = data['interest_cont_IC'].values 

        ob_vol = AskVol+BidVol
        factor = np.corrcoef(ob_vol[-120:], Interest[-120:])[0,1]
        return  factor
    
