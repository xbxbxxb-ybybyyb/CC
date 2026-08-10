import numpy as np
from future_factor import FutureFactor

class MinuteIndexNetBuyRtnDiff(FutureFactor):
    '''
    Description: (mean(ret[net_buy < 0]) - mean(ret[net_buy > 0])) / std(ret),
                 where ret = close[-1] / close[-30] - 1, net_buy = sum(BuyTradeMoney[-30:]) - sum(SellTradeMoney[-30:])          
    Class: Group_Stat
    Author: hefj, modified by lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor', 'close', 'BuyTradeMoney', 'SellTradeMoney']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 60
        adjfactor = data['adjfactor'].values
        close = data['close'].values * adjfactor
        close[close == 0] = np.nan
        buy = data['BuyTradeMoney'].values
        sell = data['SellTradeMoney'].values
        
        close_temp = close[-lb:]
        rtn_temp = close_temp[-1] / close_temp[0] - 1
        net_buy_temp = np.nansum(buy[-lb:], axis=0) - np.nansum(sell[-lb:], axis=0)
        f = (np.nanmean(rtn_temp[net_buy_temp < 0]) - np.nanmean(rtn_temp[net_buy_temp > 0])) / np.nanstd(rtn_temp)
        
        if np.isnan(f) or np.isinf(f):
            return 0
        else:
            return f