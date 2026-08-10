import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_25_srch(FutureFactor):
    # ts_argmax(ts_argmin(bun_r, 30), 100) * ts_decay_linear(bbn_2_to_bun_w, 20)
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_bigorder_count', 'BuyUniqueOrderNum', 'SellUniqueOrderNum', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy_bigorder_count = data['buy_bigorder_count'].values[-130:]
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-130:]
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-130:]
        weight = data['weight'].values[-130:]
        
        bun_r = np.nansum(BuyUniqueOrderNum, axis=1) / replace_zero(np.nansum(BuyUniqueOrderNum + SellUniqueOrderNum, axis=1))
        bbn_2_to_bun_w = np.nansum(buy_bigorder_count / replace_zero(BuyUniqueOrderNum) * weight, axis=1)
        
        factor = ts_argmax(ts_argmin(bun_r, 30), 100) * ts_decay_linear(bbn_2_to_bun_w, 20)
        return factor[-1]