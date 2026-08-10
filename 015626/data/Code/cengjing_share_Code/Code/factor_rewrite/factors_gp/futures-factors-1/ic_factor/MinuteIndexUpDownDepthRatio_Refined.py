import numpy as np
from future_factor import FutureFactor

class MinuteIndexUpDownDepthRatio_Refined(FutureFactor):
    '''
    Description: ts_mean(cs_mean(depth(r>0)) / cs_mean(depth(r<0)))
                 depth = (AskP0 - AskP4) / (BidP0 - BidP4)
    Class: Bid_Ask
    Author: jinpx, modified by jinpx
    '''
    data_type = 'IndexStock'
    instrument_type = 'main'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'adjfactor', 'BidP0', 'BidP4', 'AskP0', 'AskP4']
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        close = data['close'].values
        adjfactor = data['adjfactor'].values
        bid_0_price = data['BidP0'].values
        bid_4_price = data['BidP4'].values
        ask_0_price = data['AskP0'].values
        ask_4_price = data['AskP4'].values
        
        close_adj = close * adjfactor        
        r = np.diff(close_adj, axis=0) / close_adj[:-1] 

        N1 = 20
        N2 = 5
        N = N1 + N2

        ask_depth = ask_0_price[-N:] - ask_4_price[-N:]
        bid_depth = bid_0_price[-N:] - bid_4_price[-N:]
        depth = ask_depth / bid_depth
        depth[np.isinf(depth)] = np.nan

        depth_up_down_ratio_list = []
        for i in range(1, N2):
            r_mean = np.nanmean(r[-(N1+i):-i], axis=1)
            depth_mean = np.nanmean(depth[-(N1+i):-i], axis=1)
            depth_up_down_ratio = np.nanmean(depth_mean[r_mean>0]) / np.nanmean(depth_mean[r_mean<0])
            depth_up_down_ratio_list.append(depth_up_down_ratio) 
        f = np.nanmean(depth_up_down_ratio_list)
        if np.isnan(f):
            f = 1
            
        return f