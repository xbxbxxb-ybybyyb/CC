import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_32_srch(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['sell_bigorder_money_v2', 'SellTradeMoney', 'buy_smallorder_money', 'sell_smallorder_money_v2']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        sell_bigorder_money_v2 = data['sell_bigorder_money_v2'].values[-31:]
        SellTradeMoney = data['SellTradeMoney'].values[-31:]
        buy_smallorder_money = data['buy_smallorder_money'].values[-31:]
        sell_smallorder_money_v2 = data['sell_smallorder_money_v2'].values[-31:]
                
        sba_2_to_sa = np.nansum(sell_bigorder_money_v2, axis=1) / np.nansum(SellTradeMoney, axis=1)
        bba_4_r = np.nansum(buy_smallorder_money, axis=1) / np.nansum(buy_smallorder_money + sell_smallorder_money_v2, axis=1)
        factor = -ts_maxmin_distance(add2(sba_2_to_sa, bba_4_r), 31)[-1]
        
        return factor