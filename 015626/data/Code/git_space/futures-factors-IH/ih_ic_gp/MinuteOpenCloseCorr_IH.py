import numpy as np
from future_factor import FutureFactor

class MinuteOpenCloseCorr_IH(FutureFactor):
    '''
    Description: corr(open, close, 60)
    Class: Price_Stat
    Author: jinpx, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IH':['open', 'close']}
    normalize_size = 3 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
                
        open_price = data['open_cont_IH'].values
        close_price = data['close_cont_IH'].values
        
        N = 60
        f = np.corrcoef(open_price[-N:], close_price[-N:])[0, 1]
        
        return f