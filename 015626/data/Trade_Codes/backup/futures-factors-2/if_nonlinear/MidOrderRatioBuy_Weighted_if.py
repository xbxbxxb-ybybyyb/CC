import numpy as np
from operators_cc import *
from future_factor import FutureFactor


class MidOrderRatioBuy_Weighted_if(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight', 'buy_superorder_count', 'buy_bigorder_count', 'buy_midorder_count', 'buy_smallorder_count']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        sup = data['buy_superorder_count'].fillna(0).values[-1]
        big = data['buy_bigorder_count'].fillna(0).values[-1]
        mid = data['buy_midorder_count'].fillna(0).values[-1]
        small = data['buy_smallorder_count'].fillna(0).values[-1]
        weight = data['weight'].values[-1]
        
        temp = cross4_if(sup + big + mid + small)
        factor = np.nanmean(weight * mid / temp)
        return factor
