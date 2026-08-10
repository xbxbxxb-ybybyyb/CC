from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class Minute60BidAskVolRatio_IH(FutureFactor):
    '''
    Description: mean(BidVol, 60) / mean(AskVol, 60)
    Class: MTM
    Author: lixr, modified by shentq
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IH': ['BidVol', 'AskVol']}
    normalize_size = 60 * 240
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n = 60
        bid_vol = data['BidVol_cont_IH'].values[-n:]
        ask_vol = data['AskVol_cont_IH'].values[-n:]

        bid_ask_vol_ratio = np.nanmean(ask_vol[-n:]) / np.nanmean(bid_vol[-n:])

        return bid_ask_vol_ratio