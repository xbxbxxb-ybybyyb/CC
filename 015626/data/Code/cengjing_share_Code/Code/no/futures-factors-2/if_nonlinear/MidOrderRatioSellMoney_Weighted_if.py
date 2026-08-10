import numpy as np
from operators_cc import *
from future_factor import FutureFactor


class MidOrderRatioSellMoney_Weighted_if(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight', 'sell_superorder_money', 'sell_bigorder_money', 'sell_midorder_money', 'sell_smallorder_money']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        sup = data['sell_superorder_money'].fillna(0).values[-1]
        big = data['sell_bigorder_money'].fillna(0).values[-1]
        mid = data['sell_midorder_money'].fillna(0).values[-1]
        small = data['sell_smallorder_money'].fillna(0).values[-1]
        weight = data['weight'].values[-1]

        temp = cross4_if(sup + big + mid + small)
        factor = np.nanmean(weight * mid / temp)
        
        return factor
