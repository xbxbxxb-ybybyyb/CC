import numpy as np
from operators_cc import *
from future_factor import FutureFactor


class MidOrderRatioSell_if_IH(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['sell_superorder_count', 'sell_bigorder_count', 'sell_midorder_count', 'sell_smallorder_count']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        sup = data['sell_superorder_count'].fillna(0).values[-1]
        big = data['sell_bigorder_count'].fillna(0).values[-1]
        mid = data['sell_midorder_count'].fillna(0).values[-1]
        small = data['sell_smallorder_count'].fillna(0).values[-1]

        temp = cross4_if(sup + big + mid + small)
        factor = np.nanmean(mid / temp)
        
        return factor
