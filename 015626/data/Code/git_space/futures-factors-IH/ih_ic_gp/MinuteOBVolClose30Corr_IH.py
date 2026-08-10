import numpy as np
import pandas as pd
from future_factor import FutureFactor
from scipy.stats import skew



class  MinuteOBVolClose30Corr_IH(FutureFactor):
    '''
    Description: -corr(ClosePx, AskVol + BidVol, 30)
    Class: PV_Corr
    Author:  shentq modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Continuous_Data'] = {'IH': ['AskVol', 'BidVol','close']}

    normalize_size=20*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        AskVol = data['AskVol_cont_IH'].values 
        BidVol = data['BidVol_cont_IH'].values 
        close = data['close_cont_IH'].values 

        ob_vol = AskVol+BidVol
        factor = -np.corrcoef(ob_vol[-30:], close[-30:])[0,1]
        return  factor
    
