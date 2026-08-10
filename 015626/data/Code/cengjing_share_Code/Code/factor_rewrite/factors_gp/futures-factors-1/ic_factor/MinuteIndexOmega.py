from future_factor import FutureFactor
import numpy as np


class MinuteIndexOmega(FutureFactor):
    '''
    Description: cs_mean(omega_top_bottom),
                 omega_top_bottom = omega[(omega >= cs_rank(-omega, 10)) | (omega <= cs_rank(omega, 10))],
                 omega = positive_p / negative_p,
                 positive_p = positive_num * (positive_num - 1) / 2 * (1 / 180) ** 2,
                 negative_p = negative_num * (negative_num + 1) / 2 * (1 / 180) ** 2,
                 positive_num = ts_sum(where(pct_chg(close, 1) > 0, 1, 0), 180),
                 negative_num = ts_sum(where(pct_chg(close, 1) < 0, 1, 0), 180).
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
        close = data['close'].values[-181:]
        adj = data['adjfactor'].values[-181:]
        close = close * adj
        close[close == 0] = np.nan
        rtn = np.diff(close, axis=0) / close[:-1]
        positive_num = np.sum(rtn > 0, axis=0)
        negative_num = np.sum(rtn < 0, axis=0)
        omega_list = []
        for j in range(rtn.shape[1]):
            rtn_sorted = np.sort(rtn[:, j])
            cdf = np.arange(0, 1, 1 / len(rtn_sorted)) + 1 / len(rtn_sorted)
            p = 1 / len(rtn_sorted)
            positive = np.sum((1 - cdf[rtn_sorted > 0]) * p)
            negative = np.sum(cdf[rtn_sorted < 0] * p)
            omega = positive / negative
            if np.isinf(omega):
                omega = np.nan
            omega_list.append(omega)
        omega_sorted = np.sort(omega_list)
        f = np.nanmean(np.append(omega_sorted[:10], omega_sorted[-10:]))
        return f
