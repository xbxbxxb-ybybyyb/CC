import numpy as np
from future_factor import FutureFactor

class MinuteCloseRtnCorr_IH(FutureFactor):
    '''
    Description: corr(pct_chg(close_000905.SH, 1), delay(close_000905.SH, 1), 60) 
                 - corr(pct_chg(close_000905.SH, 1), close_000905.SH, 60)
    Class: Price_Stat
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000016.SH':['close']}
    normalize_size = 15 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 60
        close = data['close_000016.SH'].values[-lb:]
        close[close == 0] = np.nan
        
        p = close[~np.isnan(close)]
        r = p[1:] / p[:-1] - 1
        
        return np.corrcoef(r, p[:-1])[0,1] - np.corrcoef(r, p[1:])[0,1]