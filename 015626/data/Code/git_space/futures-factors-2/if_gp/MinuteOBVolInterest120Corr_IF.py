from future_factor import FutureFactor
import numpy as np


class  MinuteOBVolInterest120Corr_IF(FutureFactor):
    '''
    Description: corr(Interest, AskVol + BidVol, 120)
    Class: Bid_Ask
    Author:  shentq modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Continuous_Data'] = {'IF':['AskVol', 'BidVol','interest']}

    normalize_size=5*240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        AskVol = data['AskVol_cont_IF'].values 
        BidVol = data['BidVol_cont_IF'].values 
        Interest = data['interest_cont_IF'].values 

        ob_vol = AskVol+BidVol
        factor = np.corrcoef(ob_vol[-237:], Interest[-237:])[0,1]
        return  factor
