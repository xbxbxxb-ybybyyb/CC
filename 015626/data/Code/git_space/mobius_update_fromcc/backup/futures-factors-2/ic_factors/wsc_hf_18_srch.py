import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_18_srch(FutureFactor):
    # ppo(-sbn_4_to_sun_w, 10, 100) + sigmoid(bba_4_to_ba) + sbn_2_to_sun
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['sell_bigorder_count_v2', 'sell_smallorder_count_v2', 'SellUniqueOrderNum',
                          'buy_smallorder_money', 'BuyTradeMoney', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        sell_bigorder_count_v2 = data['sell_bigorder_count_v2'].values[-100:]
        sell_smallorder_count_v2 = data['sell_smallorder_count_v2'].values[-100:]
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-100:]
        buy_smallorder_money = data['buy_smallorder_money'].values[-100:]
        BuyTradeMoney = data['BuyTradeMoney'].values[-100:]
        weight = data['weight'].values[-100:]

        sbn_4_to_sun_w = np.nansum(sell_smallorder_count_v2 / replace_zero(SellUniqueOrderNum) * weight, axis=1)
        bba_4_to_ba = np.nansum(buy_smallorder_money, axis=1) / replace_zero(np.nansum(BuyTradeMoney, axis=1))
        sbn_2_to_sun = np.nansum(sell_bigorder_count_v2, axis=1) / np.nansum(SellUniqueOrderNum, axis=1)
        
        factor = ppo(-sbn_4_to_sun_w, 10, 100) + sigmoid(bba_4_to_ba) + sbn_2_to_sun
        return -factor[-1]