import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_31_srch(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'SellUniqueOrderNum', 'buy_bigorder_count', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-130:]
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-130:]
        buy_bigorder_count = data['buy_bigorder_count'].values[-130:]
        weight = data['weight'].values[-130:]
                
        bun_r = np.nansum(BuyUniqueOrderNum, axis=1) / np.nansum(BuyUniqueOrderNum + SellUniqueOrderNum, axis=1)
        bbn_2_to_bun_w = np.nansum(buy_bigorder_count / replace_zero(BuyUniqueOrderNum) * weight, axis=1)
        factor = mul2(ts_argmax(ts_argmin(bun_r, 30), 100), ts_decay_linear(bbn_2_to_bun_w, 20))[-1]
        
        return factor