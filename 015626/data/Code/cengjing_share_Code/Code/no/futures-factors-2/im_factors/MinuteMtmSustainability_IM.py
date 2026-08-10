import numpy as np
from future_factor import FutureFactor

class MinuteMtmSustainability_IM(FutureFactor):
    '''
    Description: auto_corr(pct_chg(close, 1), 30) * (sum(where(close > delay(close, 1), 1, 0), 30) - 15)
    Class: MTM
    Author: liuz, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000852.SH':['close']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
                
        index_close = data['close_000852.SH'].values
        index_r = np.diff(index_close) / index_close[:-1]
        index_r_autocorr = np.corrcoef(index_r[-30:], index_r[-31:-1])[0, 1]
        counter = np.sum(index_r[-30:]>0) - 15
        f = index_r_autocorr * counter
        
        return f