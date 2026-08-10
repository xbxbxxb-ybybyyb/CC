from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class MinuteBidAskVolAutoCorr(FutureFactor):
    '''
    Description: corr(sum(AskVol,BidVol),delay(sum(AskVol,BidVol),1),60)
    Class: AutoCorr
    Author: lixr, modified by shentq
    '''
    data_type = 'Future'
    instrument_type = 'main'
    days_past = 1
    data_dict = dict()
    data_dict['Future_Data'] = ['BidVol', 'AskVol']
    normalize_size = 10 * 240
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n1 = 60
        n2 = 1
        bid_vol = data['BidVol'].values[-n1:]
        ask_vol = data['AskVol'].values[-n1:]
        bid_ask_vol_sum = bid_vol + ask_vol

        return np.corrcoef(bid_ask_vol_sum[n2:], bid_ask_vol_sum[:-n2])[0, 1]