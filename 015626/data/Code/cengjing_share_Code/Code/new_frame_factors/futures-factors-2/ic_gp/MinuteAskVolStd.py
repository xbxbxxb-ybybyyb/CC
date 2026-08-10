from future_factor import FutureFactor
import numpy as np


class MinuteAskVolStd(FutureFactor):
    '''
    Description: std(AskVol, 20) / mean(AskVol, 240)
    Class: Bid_Ask
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Future_Data'] = ['AskVol']
    normalize_size = 20 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        ask = data['AskVol'].values[-240:]
        f = np.nanstd(ask[-20:]) / np.nanmean(ask)
        return f
