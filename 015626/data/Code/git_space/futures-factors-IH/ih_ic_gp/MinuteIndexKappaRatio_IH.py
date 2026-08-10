from future_factor import FutureFactor
import numpy as np


class MinuteIndexKappaRatio_IH(FutureFactor):
    '''
    Description: cs_mean(kappa_top_bottom),
                 kappa_top_bottom = kappa[(kappa >= cs_rank(-kappa, 10)) | (kappa <= cs_rank(kappa, 10))],
                 kappa = ts_mean(diff(close * adjfactor, 1), 150) / ts_max(-diff(close * adjfactor, 1), 150).
    Class: Return_Risk
    Author: jinpx, modified by hefj
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['close', 'adjfactor']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):        
        close = data['close'].values[-151:]
        adj = data['adjfactor'].values[-151:]
        close = close * adj
        close[close == 0] = np.nan
        diff = np.diff(close, axis=0)
        kappa = np.nanmean(diff, axis=0) / np.max(-diff, axis=0)
        kappa[np.isinf(kappa)] = np.nan
        kappa_sorted = np.sort(kappa)
        f = np.nanmean(np.append(kappa_sorted[:10], kappa_sorted[-10:]))
        return f
