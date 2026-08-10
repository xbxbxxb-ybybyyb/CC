import numpy as np
from future_factor import FutureFactor

class MinuteSpotFutureAutoBeta(FutureFactor):
    '''
    Description: cov(delay(pct_chg(close_000905.SH, 1), 1), pct_chg(close, 1), 30) / var(delay(pct_chg(close_000905.SH, 1), 1), 30)
    Class: Future_Spot_Price
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Future_Data'] = ['close']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 30
        index_close = data['close_000905.SH'].values
        index_close[index_close == 0] = np.nan
        close = data['close'].values
        close[close == 0] = np.nan
        
        
        rtn = close[-lb:] / close[-lb - 1: -1] - 1
        index_rtn = index_close[-lb:] / index_close[-lb - 1: -1] - 1
        cov = np.cov(index_rtn[:-1], rtn[1:])
        f = cov[0, 1] / cov[0, 0]
        
        if np.isnan(f) or np.isinf(f):
            return 0
        else:
            return f