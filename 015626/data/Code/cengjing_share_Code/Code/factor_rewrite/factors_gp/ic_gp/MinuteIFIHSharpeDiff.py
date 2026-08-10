from future_factor import FutureFactor
import numpy as np


class MinuteIFIHSharpeDiff(FutureFactor):
    '''
    Description: sharpe(pct_chg(close_000300.SH, 1), 15) - sharpe(pct_chg(close_000016.SH, 1), 15)
    Class: Multi-Variety
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'main'
    days_past = 1
    data_dict = {}
    data_dict['Index_Id'] = {'000300.SH': ['close'], '000016.SH': ['close']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        close_hs = data['close_000300.SH'].values[-16:]
        close_sz = data['close_000016.SH'].values[-16:]
        r_hs = (close_hs[1:] - close_hs[:-1]) / close_hs[:-1]
        r_sz = (close_sz[1:] - close_sz[:-1]) / close_sz[:-1]
        f = np.nanmean(r_hs) / np.nanstd(r_hs) - np.nanmean(r_sz) / np.nanstd(r_sz)
        return f
