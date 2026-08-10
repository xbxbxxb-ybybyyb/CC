import numpy as np
from future_factor import FutureFactor

class MinuteIndexUpDownTotalValueTradeRatio_IH(FutureFactor):
    '''
    Description: ts_mean(cs_mean(totalvaluetrade(r>0)) / cs_mean(totalvaluetrade(r<0)))
    Class: PV_Corr
    Author: jinpx, modified by jinpx
    '''
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'adjfactor', 'TotalValueTrade']
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        close = data['close'].values
        adjfactor = data['adjfactor'].values
        totalvaluetrade = data['TotalValueTrade'].values
        
        close_adj = close * adjfactor
        r = np.diff(close_adj, axis=0) / close_adj[:-1]
        
        N = 5
        totalvaluetrade_ratio = np.array([])
        for i in range(N):
            totalvaluetrade_ratio = np.append(totalvaluetrade_ratio, np.nanmean(totalvaluetrade[-i][r[-i]>0])/np.nanmean(totalvaluetrade[-i][r[-i]<0]))

        f = np.nanmean(totalvaluetrade_ratio)
            
        return f