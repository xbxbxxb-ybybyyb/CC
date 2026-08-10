import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_33_srch(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['sell_smallorder_count_v2', 'SellUniqueOrderNum', 'buy_bigorder_money', 'sell_bigorder_money_v2', 'buy_smallorder_money', 'sell_smallorder_money_v2', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        sell_smallorder_count_v2 = data['sell_smallorder_count_v2'].values[-45:]
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-45:]
        buy_bigorder_money = data['buy_bigorder_money'].values[-45:]
        sell_bigorder_money_v2 = data['sell_bigorder_money_v2'].values[-45:]
        buy_smallorder_money = data['buy_smallorder_money'].values[-45:]
        sell_smallorder_money_v2 = data['sell_smallorder_money_v2'].values[-45:]
        weight = data['weight'].values[-45:]
                
        sbn_4_to_sun = np.nansum(sell_smallorder_count_v2, axis=1) / replace_zero(np.nansum(SellUniqueOrderNum, axis=1))
        bba_2_r_w = np.nansum(buy_bigorder_money / replace_zero(buy_bigorder_money + sell_bigorder_money_v2) * weight, axis=1)
        bba_4_r = np.nansum(buy_smallorder_money, axis=1) / np.nansum(buy_smallorder_money + sell_smallorder_money_v2, axis=1)
        factor = aroon(sbn_4_to_sun, sub2(bbands_down(bba_2_r_w, 15), bba_4_r), 30)[-1]
        
        return factor