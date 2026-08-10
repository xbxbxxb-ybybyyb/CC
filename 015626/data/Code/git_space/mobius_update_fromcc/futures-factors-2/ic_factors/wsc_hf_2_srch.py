import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_2_srch(FutureFactor):
    # -min2(max2(aroon(ba_r, ts_maxmin_distance(bn_r, 25), 70), ts_maxmin_distance(bun_r, 25)), ts_max(bun_to_bn_w, 5))
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeMoney', 'SellTradeMoney', 'BuyTradeNum', 'SellTradeNum', 
                          'BuyUniqueOrderNum', 'SellUniqueOrderNum', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        BuyTradeMoney = data['BuyTradeMoney'].values[-100:]
        SellTradeMoney = data['SellTradeMoney'].values[-100:]
        BuyTradeNum = data['BuyTradeNum'].values[-100:]
        SellTradeNum = data['SellTradeNum'].values[-100:]
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-100:]
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-100:]
        weight = data['weight'].values[-100:]
        
        ba = np.nansum(BuyTradeMoney, axis=1)
        sa = np.nansum(SellTradeMoney, axis=1)
        bn = np.nansum(BuyTradeNum, axis=1)
        sn = np.nansum(SellTradeNum, axis=1)
        bun = np.nansum(BuyUniqueOrderNum, axis=1)
        sun = np.nansum(SellUniqueOrderNum, axis=1)
        ba_r = ba / replace_zero(ba + sa)
        bn_r = bn / replace_zero(bn + sn)
        bun_r = bun / replace_zero(bun + sun)
        bun_to_bn_w = np.nansum(BuyUniqueOrderNum / replace_zero(BuyTradeNum) * weight, axis=1)
        
        temp_1 = aroon(ba_r, ts_maxmin_distance(bn_r, 25), 70)[-1]
        temp_2 = ts_maxmin_distance(bun_r, 25)[-1]
        temp_3 = ts_max(bun_to_bn_w, 5)[-1]
        factor = min(max(temp_1, temp_2), temp_3)        
        return -factor