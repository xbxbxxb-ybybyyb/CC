from scipy import stats
import pandas as pd
import numpy as np
import bottleneck as bn
from future_factor import FutureFactor


class MinuteIndexBidAskVolSkewRatio_IH(FutureFactor):
    '''
    Description: -cs_skew(TotalBidVol[-1]) / skew(TotalAskVol[-1])
    Class: Bid_Ask
    Author: lixr, modified by shentq
    '''
    data_type = 'IndexStock'
    days_past = 0
    data_dict = dict()
    data_dict['Stock'] = ['TotalBidVol', 'TotalAskVol']
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        total_bid_vol = data['TotalBidVol'].values[-1]
        total_ask_vol = data['TotalAskVol'].values[-1]

        skew_bid = stats.skew(total_bid_vol, nan_policy='omit')
        skew_ask = stats.skew(total_ask_vol, nan_policy='omit')

        return -skew_bid / skew_ask