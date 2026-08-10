from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class MinuteIndexWeightedBidAskTotalVolRatio(FutureFactor):
    '''
    Description: weighted_cs_mean(TotalBidVol[-1], w=index_weight) / weighted_cs_mean(TotalAskVol[-1], w=index_weight)
    Class: Group_Stat
    Author: lixr, modified by shentq
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['TotalBidVol', 'TotalAskVol', 'weight']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):

        weight_ratio = data['weight'].values[-1] / np.nansum(data['weight'].values[-1])

        buy = np.nansum(data['TotalBidVol'].values[-1] * weight_ratio)
        sell = np.nansum(data['TotalAskVol'].values[-1] * weight_ratio)

        if sell == 0:
            factor_value = 0
        else:
            factor_value = buy / sell

        return factor_value