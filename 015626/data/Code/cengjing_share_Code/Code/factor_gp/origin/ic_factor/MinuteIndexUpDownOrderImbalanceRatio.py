import numpy as np
from future_factor import FutureFactor

class MinuteIndexUpDownOrderImbalanceRatio(FutureFactor):
    '''
    Description: ts_mean(ts_mean(where(cs_mean(pct_chg(ClosePx, 1)) > 0, cs_mean((sum(BidVi, i=0,1,…4) - sum(AskVi, i=0,1,…,4)) / ((sum(BidVi, i=0,1,…,4) + sum(AskVi, i=0,1,…,4))), nan), 20)
    Class: Bid_Ask
    Author: jinpx, modified by jinpx
    '''
    data_type = 'IndexStock'
    instrument_type = 'main'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'adjfactor', 'BidV0', 'BidV1', 'BidV2', 'BidV3', 'BidV4', 'AskV0', 'AskV1', 'AskV2', 'AskV3', 'AskV4']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        close = data['close'].values
        adjfactor = data['adjfactor'].values
        bid_0_volume = data['BidV0'].values
        bid_1_volume = data['BidV1'].values
        bid_2_volume = data['BidV2'].values
        bid_3_volume = data['BidV3'].values
        bid_4_volume = data['BidV4'].values
        ask_0_volume = data['AskV0'].values
        ask_1_volume = data['AskV1'].values
        ask_2_volume = data['AskV2'].values
        ask_3_volume = data['AskV3'].values
        ask_4_volume = data['AskV4'].values
        
        close_adj = close * adjfactor        
        r = np.diff(close_adj, axis=0) / close_adj[:-1] 

        N1 = 20
        N2 = 10
        N = N1 + N2
        bid_volume = bid_0_volume[-N:] + bid_1_volume[-N:] + bid_2_volume[-N:] + bid_3_volume[-N:] + bid_4_volume[-N:]
        ask_volume = ask_0_volume[-N:] + ask_1_volume[-N:] + ask_2_volume[-N:] + ask_3_volume[-N:] + ask_4_volume[-N:]
        order_imbalance = (bid_volume - ask_volume) / (bid_volume + ask_volume)

        order_imbalance_up_down_ratio_list = []
        for i in range(1, N2+1):
            r_mean = np.nanmean(r[-(N1+i):-i], axis=1)
            order_imbalance_mean = np.nanmean(order_imbalance[-(N1+i):-i], axis=1)
            order_imbalance_up_down_ratio = np.nanmean(order_imbalance_mean[r_mean>0]) / np.nanmean(order_imbalance_mean[r_mean<0])
            order_imbalance_up_down_ratio_list.append(order_imbalance_up_down_ratio) 

        f = np.nanmean(order_imbalance_up_down_ratio_list)
        if np.isnan(f):
            f = 1
            
        return f