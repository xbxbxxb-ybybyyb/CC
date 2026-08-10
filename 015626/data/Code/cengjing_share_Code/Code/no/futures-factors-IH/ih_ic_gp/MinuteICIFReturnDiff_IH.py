from future_factor import FutureFactor
import numpy as np


class MinuteICIFReturnDiff_IH(FutureFactor):
    '''
    Description: mean(pct_chg(close_000905.SH, 1) - pct_chg(close_000300.SH, 1), 15)
    Class: Multi-Variety
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Index_Id'] = {'000905.SH': ['close'], '000016.SH': ['close']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        close_zz = data['close_000905.SH'].values[-16:]
        close_hs = data['close_000016.SH'].values[-16:]
        r_zz = (close_zz[1:] - close_zz[:-1]) / close_zz[:-1]
        r_hs = (close_hs[1:] - close_hs[:-1]) / close_hs[:-1]
        f = np.nanmean(r_zz - r_hs)
        return f
