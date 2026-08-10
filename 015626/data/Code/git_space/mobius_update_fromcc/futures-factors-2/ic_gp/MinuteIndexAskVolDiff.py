from future_factor import FutureFactor
import numpy as np


class MinuteIndexAskVolDiff(FutureFactor):
    '''
    Description: cs_mean(ts_mean(pct_chg(TotalAskVol / adjfactor, 1), 20))
    Class: Bid_Ask
    Author: jinpx, modified by hefj
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['TotalAskVol', 'adjfactor']
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        ask = data['TotalAskVol'].values[-21:]
        ask[ask == 0] = np.nan
        adj = data['adjfactor'].values[-21:]
        adj[adj == 0] = np.nan
        ask = ask / adj
        ask_g = np.nanmean(np.diff(ask, n=1, axis=0) / ask[:-1], axis=0)
        f = -np.nanmean(ask_g)
        return f
