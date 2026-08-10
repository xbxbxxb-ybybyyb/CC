from future_factor import FutureFactor
import numpy as np


class MinuteAskBidDiffStd(FutureFactor):
    '''
    Description: std(AskVol, 40) / mean(AskVol + BidVol, 240)
    Class: Bid_Ask
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Future_Data'] = ['AskVol', 'BidVol']
    normalize_size = 20 * 240
    normalize_type = 'ts_rank'

    def calculate(self, data):
        ask = data['AskVol'].values[-240:]
        bid = data['BidVol'].values[-240:]
        f = np.nanstd(ask[-40:] - bid[-40]) / np.nanmean(ask + bid)
        return f
