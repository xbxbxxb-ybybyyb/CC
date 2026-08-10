import numpy as np
from future_factor import FutureFactor

class MinuteUpDownAutoCorrDiff(FutureFactor):
    '''
    Description: corr(where(delay(close_000905.SH, 1) > delay(close_000905.SH, 2), delay(pct_chg(close_000905.SH, 1), 1), nan),
                where(delay(close_000905.SH, 1) > delay(close_000905.SH, 2), pct_chg(close, 1), nan), 35)
                - corr(where(delay(close_000905.SH, 1) < delay(close_000905.SH, 2), delay(pct_chg(close_000905.SH, 1), 1), nan),
                where(delay(close_000905.SH, 1) < delay(close_000905.SH, 2), pct_chg(close, 1), nan), 35)
    Class: Future_Spot_Price
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'main'
    days_past = 1
    data_dict = dict()
    data_dict['Future_Data'] = ['close']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 35
        close = data['close'].values
        close[close == 0] = np.nan
        idx_close = data['close_000905.SH'].values
        idx_close[idx_close == 0] = np.nan   

        rtn = close[-lb - 1:] / close[-lb - 2: -1] - 1
        rtn[np.isnan(rtn)] = 0
        idx_rtn = idx_close[-lb - 1:] / idx_close[-lb - 2: -1] - 1
        idx_rtn[np.isnan(idx_rtn)] = 0
        up = idx_rtn[:-1] > 0
        down = idx_rtn[:-1] < 0
        corr_up = np.corrcoef(idx_rtn[:-1][up], rtn[1:][up])[0,1]
        corr_down = np.corrcoef(idx_rtn[:-1][down], rtn[1:][down])[0,1]
        f = corr_up - corr_down
        
        if np.isnan(f) or np.isinf(f):
            return 0
        else:
            return f