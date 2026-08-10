import numpy as np
from operators_cc import *
from future_factor import FutureFactor


class SellUnique_Weighted_if(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight', 'SellUniqueOrderNum', 'SellTradeNum']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-1]
        SellTradeNum = data['SellTradeNum'].values[-1]
        weight = data['weight'].values[-1]

        a = cross_if(weight * SellUniqueOrderNum / SellTradeNum)
        factor = np.nanmean(a)
        
        return factor
