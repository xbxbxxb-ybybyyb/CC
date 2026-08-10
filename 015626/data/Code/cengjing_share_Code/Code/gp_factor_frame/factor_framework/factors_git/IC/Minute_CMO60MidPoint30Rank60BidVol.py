from scipy import stats
import pandas as pd
import numpy as np
import bottleneck as bn
from future_factor import FutureFactor


class Minute_CMO60MidPoint30Rank60BidVol(FutureFactor):
    '''
    Description: CMO_60(MidPoint_30(Rank_60(BidVol)))
    Class: gpLearn
    Author: lixr, modified by shentq
    '''
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Future_Data'] = ['BidVol']
    normalize_size = 1 * 240
    normalize_type = 'ts_rank'

    def calculate(self, data):
        rank_60 = data['BidVol'].rolling(60).apply(lambda x: x.searchsorted(x[-1], sorter=np.argsort(x)),
                                                   raw=True).fillna(0).values
        rank_60[np.isnan(rank_60)] = 0

        mid_point_30 = (bn.move_max(rank_60, 30) + bn.move_min(rank_60, 30)) / 2
        mid_point_30[np.isnan(mid_point_30)] = 0

        mid_point_rtn = mid_point_30[-60:] / mid_point_30[-61:-1] - 1
        mid_point_rtn[np.isinf(mid_point_rtn)] = np.nan

        pos_rtn = np.copy(mid_point_rtn)
        pos_rtn[pos_rtn < 0] = 0

        neg_rtn = np.copy(mid_point_rtn)
        neg_rtn[neg_rtn > 0] = 0

        pos_rtn_sum = np.nansum(pos_rtn[-60:])
        neg_rtn_sum = np.nansum(-neg_rtn[-60:])

        factor_value = (pos_rtn_sum - neg_rtn_sum) / (pos_rtn_sum + neg_rtn_sum)

        return factor_value
