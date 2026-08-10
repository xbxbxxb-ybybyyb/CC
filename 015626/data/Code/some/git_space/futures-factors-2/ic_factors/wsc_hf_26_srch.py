import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_26_srch(FutureFactor):
    # min2(ts_maxmin_distance(sbn_4_to_sun_w, 30), midprice(sbn_4_to_sun, bba_2_to_ba_w, 20))
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['sell_smallorder_count_v2', 'SellUniqueOrderNum', 'weight', 'buy_bigorder_money', 
                          'BuyTradeMoney']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        sell_smallorder_count_v2 = data['sell_smallorder_count_v2'].values[-30:]
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-30:]
        weight = data['weight'].values[-30:]
        buy_bigorder_money = data['buy_bigorder_money'].values[-30:]
        BuyTradeMoney = data['BuyTradeMoney'].values[-30:]
        
        sbn_4_to_sun_w = np.nansum(sell_smallorder_count_v2 / replace_zero(SellUniqueOrderNum) * weight, axis=1)
        sbn_4_to_sun = np.nansum(sell_smallorder_count_v2, axis=1) / replace_zero(np.nansum(SellUniqueOrderNum, axis=1))
        bba_2_to_ba_w = np.nansum(buy_bigorder_money / replace_zero(BuyTradeMoney) * weight, axis=1)
        
        factor = min2(ts_maxmin_distance(sbn_4_to_sun_w, 30), midprice(sbn_4_to_sun, bba_2_to_ba_w, 20))
        return factor[-1]