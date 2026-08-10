import numpy as np
import pandas as pd
from future_factor import FutureFactor
from scipy.stats import skew



class  MinuteVolSpreadInterestCorr_IH(FutureFactor):
    '''
    Description: 
    Class:Liquidity
    Author: lixr modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Continuous_Data'] = {'IH':['AskVol', 'BidVol','interest']}

    normalize_size=20*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        AskVol = data['AskVol_cont_IH'].values 
        BidVol = data['BidVol_cont_IH'].values 
        Interest = data['interest_cont_IH'].values 

        vol_spread = BidVol-AskVol
        factor = -np.corrcoef(vol_spread[-120:], Interest[-120:])[0,1]
        return  factor
    