import numpy as np
from future_factor import FutureFactor

class MinuteIndexAskBidVolRatioStd(FutureFactor):
    '''
    Description: ts_mean(cs_std(TotalBidVol / TotalAskVol), 10)
    Class: Bid_Ask
    Author: jinpx, modified by jinpx
    '''
    data_type = 'IndexStock'
    instrument_type = 'main'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['TotalBidVol', 'TotalAskVol']
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        totalbidvol = data['TotalBidVol'].values
        totalaskvol = data['TotalAskVol'].values

        N = 10
        total_bid_ask_vol_ratio = totalbidvol[-N:] / totalaskvol[-N:]
        total_bid_ask_vol_ratio[np.isinf(total_bid_ask_vol_ratio)] = np.nan
        f = np.nanmean(np.nanstd(total_bid_ask_vol_ratio, axis=1))
        
        return f