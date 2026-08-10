from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class MinuteIndex20WeightedReturnSkew(FutureFactor):
    '''
    Description: weighted_cs_skew(pct_chg(ClosePx,1),w=index_weight)
    Class: Price_CS_Stat
    Author: lixr, modified by shentq
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'adjfactor', 'weight']
    normalize_size = 15 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        close = data['close'].values
        adjfactor = data['adjfactor'].values
        weight = data['weight'].values

        close_adj = close * adjfactor
        close_adj[close_adj == 0] = np.nan

        rtn = close_adj[-1] / close_adj[-21] - 1
        weighted_mean = np.nansum(rtn * weight[-1])
        weighted_std = np.nansum(weight[-1] * (rtn - weighted_mean) ** 2) ** 0.5

        return np.nansum(weight[-1] * (rtn - weighted_mean) ** 3) / (weighted_std ** 3)