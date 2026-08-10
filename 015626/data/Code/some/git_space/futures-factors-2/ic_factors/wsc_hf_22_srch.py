import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_22_srch(FutureFactor):
    # (bun_to_bn + auto_corr(bun_to_bn, 60, 50)) * bba_4_r_w / bba_2_r_w
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'BuyTradeNum', 'buy_smallorder_money', 'sell_smallorder_money_v2',
                          'buy_bigorder_money', 'sell_bigorder_money_v2', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-111:]
        BuyTradeNum = data['BuyTradeNum'].values[-111:]
        buy_smallorder_money = data['buy_smallorder_money'].values[-111:]
        sell_smallorder_money_v2 = data['sell_smallorder_money_v2'].values[-111:]
        buy_bigorder_money = data['buy_bigorder_money'].values[-111:]
        sell_bigorder_money_v2 = data['sell_bigorder_money_v2'].values[-111:]
        weight = data['weight'].values[-111:]

        bun_to_bn = np.nansum(BuyUniqueOrderNum, axis=1) / replace_zero(np.nansum(BuyTradeNum, axis=1))
        bba_4_r_w = np.nansum(buy_smallorder_money / replace_zero(buy_smallorder_money + sell_smallorder_money_v2) * weight, axis=1)
        bba_2_r_w = np.nansum(buy_bigorder_money / replace_zero(buy_bigorder_money + sell_bigorder_money_v2) * weight, axis=1)
        
        factor = (bun_to_bn + auto_corr(bun_to_bn, 60, 50)) * bba_4_r_w / bba_2_r_w
        return -factor[-1]