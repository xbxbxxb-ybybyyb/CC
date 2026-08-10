from future_factor import FutureFactor
import numpy as np


class MinuteIFIHReturnDiff_IH(FutureFactor):
    '''
    Description: mean(pct_chg(close_000300.SH, 1) - pct_chg(close_000016.SH, 1), 30)
    Class: Multi-Variety
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Index_Id'] = {'000300.SH': ['close'], '000016.SH': ['close']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        close_hs = data['close_000300.SH'].values[-31:]
        close_sz = data['close_000016.SH'].values[-31:]
        r_hs = (close_hs[1:] - close_hs[:-1]) / close_hs[:-1]
        r_sz = (close_sz[1:] - close_sz[:-1]) / close_sz[:-1]
        f = np.nanmean(r_hs - r_sz)
        return f
