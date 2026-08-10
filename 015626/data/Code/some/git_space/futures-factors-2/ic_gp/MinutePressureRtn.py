import numpy as np
from future_factor import FutureFactor

class MinutePressureRtn(FutureFactor):
    '''
    Description: 
    Class: Bid_Ask
    Author: liuz, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close', 'AskVol', 'BidVol']}
    normalize_size = 60
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        close = data['close_cont_IC'].values
        askvol = data['AskVol_cont_IC'].values
        bidvol = data['BidVol_cont_IC'].values
        
        N = 60
        r = (np.diff(close) / close[:-1])[-N:]
        bid_ask_vol_diff = (bidvol - askvol)[-(N+1):-1]

        f = np.nansum((r<0) & (bid_ask_vol_diff<0))/np.nansum(r<0) - np.nansum((r>0)&(bid_ask_vol_diff>0))/np.nansum(r>0)
        
        return f