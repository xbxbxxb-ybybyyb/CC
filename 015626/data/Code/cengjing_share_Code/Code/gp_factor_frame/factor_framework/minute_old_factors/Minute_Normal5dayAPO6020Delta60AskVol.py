from scipy import stats
import pandas as pd
import numpy as np
import bottleneck as bn
from future_factor import FutureFactor


class Minute_Normal5dayAPO6020Delta60AskVol(FutureFactor):
    '''
    Description: APO_60_20(Delta_60(AskVol))
    Class: gpLearn
    Author: lixr, modified by shentq
    '''
    data_type = 'Future'
    days_past = 60
    data_dict = dict()
    data_dict['Future_Data'] = ['AskVol']
    normalize_size = 10 * 240
    normalize_type = 'ts_rank'

    def calculate(self, data):
        ask_vol = data['AskVol'].values

        ask_vol_delta_60 = ask_vol[60:] - ask_vol[:-60]
        apo = bn.move_mean(ask_vol_delta_60, 20) - bn.move_mean(ask_vol_delta_60, 60)

        apo_mean = np.nanmean(apo[-5 * 240 - 1:-1])
        apo_std = np.nanstd(apo[-5 * 240 - 1:-1])

        factor_value = (apo[-1] - apo_mean) / apo_std

        if np.isnan(factor_value):
            factor_value = 0

        return factor_value