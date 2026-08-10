import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_24_srch_if(FutureFactor):
    # -midprice(bba_4_r, coefficient_of_variation(bba_2_r_w, 25), 5)
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight', 'buy_smallorder_money', 'sell_smallorder_money_v2', 'buy_bigorder_money', 
                          'sell_bigorder_money_v2']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        weight = data['weight'].values[-30:]
        buy_smallorder_money = data['buy_smallorder_money'].values[-30:]
        sell_smallorder_money_v2 = data['sell_smallorder_money_v2'].values[-30:]
        buy_bigorder_money = data['buy_bigorder_money'].values[-30:]
        sell_bigorder_money_v2 = data['sell_bigorder_money_v2'].values[-30:]
        
        bba_4_r = np.nansum(buy_smallorder_money, axis=1) / replace_zero(np.nansum(buy_smallorder_money + sell_smallorder_money_v2, axis=1))
        bba_2_r_w = np.nansum(buy_bigorder_money / replace_zero(buy_bigorder_money + sell_bigorder_money_v2) * weight, axis=1)
        
        factor = -midprice(bba_4_r, coefficient_of_variation(bba_2_r_w, 25), 5)
        return factor[-1]