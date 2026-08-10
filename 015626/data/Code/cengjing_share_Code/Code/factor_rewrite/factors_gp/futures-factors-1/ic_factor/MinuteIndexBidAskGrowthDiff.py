from future_factor import FutureFactor
import numpy as np


class MinuteIndexBidAskGrowthDiff(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['TotalAskVol', 'TotalBidVol', 'adjfactor', 'weight']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 30
        weight = data['weight'].values[-lb:]
        adj = data['adjfactor'].values[-lb:]
        ask = data['TotalAskVol'].values[-lb:] / adj * adj[-1]
        ask[ask == 0] = np.nan
        bid = data['TotalBidVol'].values[-lb:] / adj * adj[-1]
        bid[bid == 0] = np.nan
        nan_num = np.isnan(ask).sum(axis=0) + np.isnan(bid).sum(axis=0)
        ask = ask[:, nan_num == 0]
        bid = bid[:, nan_num == 0]
        ask_diff = ask[1:] - ask[:-1]
        bid_diff = bid[1:] - bid[:-1]
        diff_ratio = (bid_diff - ask_diff) / (np.abs(bid_diff) + np.abs(ask_diff))
        f = np.nanmean(np.nansum(diff_ratio * weight[1:, nan_num == 0], axis=1))
        return f
