import numpy as np
from future_factor import FutureFactor

class MinuteICIFAskBidVolPressureDiff(FutureFactor):
    '''
    Description: 
    Class: 
    Author: jinpx
    '''
    data_type = 'Future'
    instrument_type = 'main'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC': ['AskVol', 'BidVol'], 'IF': ['AskVol', 'BidVol']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        AskVol_IC = data['AskVol_cont_IC'].values
        BidVol_IC = data['BidVol_cont_IC'].values
        AskVol_IF = data['AskVol_cont_IF'].values
        BidVol_IF = data['BidVol_cont_IF'].values
        
        pressure_IC = AskVol_IC - BidVol_IC
        pressure_IF = AskVol_IF - BidVol_IF
        
        N = 10
        f = np.nanmean(pressure_IC[-N:]) - np.nanmean(pressure_IF[-N:])
        
        return f