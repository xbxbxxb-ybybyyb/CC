import numpy as np
from operators_cc import *
from future_factor import FutureFactor
from help_functions_wsc import replace_zero


class MidOrderRatioSellMoney_5_if(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['sell_superorder_money', 'sell_bigorder_money', 'sell_midorder_money', 'sell_smallorder_money']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        sup = data['sell_superorder_money'].fillna(0).iloc[-5:]
        big = data['sell_bigorder_money'].fillna(0).iloc[-5:]
        mid = data['sell_midorder_money'].fillna(0).iloc[-5:]
        small = data['sell_smallorder_money'].fillna(0).iloc[-5:]
        
        date = str(sup.index[-1].date())
        sup = sup.loc[date].values
        big = big.loc[date].values
        mid = mid.loc[date].values
        small = small.loc[date].values
        
        if sup.shape[0] > 1:
            sup = np.nanmean(sup, axis = 0)
            big = np.nanmean(big, axis = 0)
            mid = np.nanmean(mid, axis = 0)
            small = np.nanmean(small, axis = 0)
        temp = cross4_if(replace_zero(sup + big + mid + small))
        factor = np.nanmean(mid / temp)
        
        return factor
