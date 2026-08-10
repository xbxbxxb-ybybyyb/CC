from future_factor import FutureFactor
import numpy as np


class MinuteOpenInterestRtnCorr(FutureFactor):
    '''
    Description: corr(close / open - 1, OpenInterest, 250)
    Class: PV_Corr
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'main'
    days_past = 2
    data_dict = {}
    data_dict['Future_Data'] = ['OpenInterest', 'close', 'open']
    normalize_size = 20 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        close = data['close'].values[-250:]
        open_px = data['open'].values[-250:]
        interest = data['OpenInterest'].values[-250:]
        f = np.corrcoef(interest, close / open_px - 1)[0, 1]
        return f
