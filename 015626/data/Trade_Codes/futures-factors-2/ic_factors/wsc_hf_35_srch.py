import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_35_srch(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['sell_midorder_count_v2', 'SellUniqueOrderNum', 'BuyUniqueOrderNum', 'BuyTradeNum', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        
        sell_midorder_count_v2 = data['sell_midorder_count_v2'].values[-65:]
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-65:]
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-65:]
        BuyTradeNum = data['BuyTradeNum'].values[-65:]
        weight = data['weight'].values[-65:]
             
        sbn_3_to_sun_w = np.nansum(sell_midorder_count_v2 / replace_zero(SellUniqueOrderNum) * weight, axis=1)
        bun_to_bn_w = np.nansum(BuyUniqueOrderNum / replace_zero(BuyTradeNum) * weight, axis=1)
        bun_r = np.nansum(BuyUniqueOrderNum, axis=1) / np.nansum(BuyUniqueOrderNum + SellUniqueOrderNum, axis=1)
        
        factor = -min2(ts_maxmin_distance(bun_r, 30), aroon(ts_max(bun_to_bn_w, 6), sbn_3_to_sun_w, 57))[-1]
        
        return factor