import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_7_srch(FutureFactor):
    # sba_4_to_sa * ts_min(bba_2_to_ba, 30) * ts_reg_alpha(sbn_3_to_sun_w, 30)
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeMoney', 'SellTradeMoney', 'SellUniqueOrderNum', 'buy_bigorder_money', 
                          'sell_smallorder_money_v2', 'sell_midorder_count_v2', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        BuyTradeMoney = data['BuyTradeMoney'].values[-32:]
        SellTradeMoney = data['SellTradeMoney'].values[-32:]
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-32:]
        buy_bigorder_money = data['buy_bigorder_money'].values[-32:]
        sell_smallorder_money_v2 = data['sell_smallorder_money_v2'].values[-32:]
        sell_midorder_count_v2 = data['sell_midorder_count_v2'].values[-32:]
        weight = data['weight'].values[-32:]
        
        sba_4_to_sa = np.nansum(sell_smallorder_money_v2, axis=1) / replace_zero(np.nansum(SellTradeMoney, axis=1))
        bba_2_to_ba = np.nansum(buy_bigorder_money, axis=1) / replace_zero(np.nansum(BuyTradeMoney, axis=1))
        sbn_3_to_sun_w = np.nansum(sell_midorder_count_v2 / replace_zero(SellUniqueOrderNum) * weight, axis=1)
        
        factor = sba_4_to_sa * ts_min(bba_2_to_ba, 30) * ts_reg_alpha(sbn_3_to_sun_w, 30)
        return factor[-1]