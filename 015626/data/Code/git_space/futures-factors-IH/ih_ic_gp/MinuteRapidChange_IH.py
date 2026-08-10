import numpy as np
from future_factor import FutureFactor

class MinuteRapidChange_IH(FutureFactor):
    '''
    Description: 
    Class: Price_Stat
    Author: jinpx, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000016.SH':['close']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
                
        index_close = data['close_000016.SH'].values
                    
        N = 45
        baseline = np.array([i/(N-1)*(index_close[-1]-index_close[-N])+index_close[-N] for i in range(N)])
        distance = (index_close[-N:] - baseline) / index_close[-N] * (index_close[-N] - index_close[-1]) / index_close[-N]

        f = np.max(distance) - np.min(distance)

        return f