import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_8_srch(FutureFactor):
    # sbn_4_to_sun_w / bba_4_to_ba_w - auto_corr(bba_1, 80, 100)
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeMoney', 'SellUniqueOrderNum', 'buy_superorder_money', 
                          'buy_smallorder_money', 'sell_smallorder_count_v2', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        BuyTradeMoney = data['BuyTradeMoney'].values[-182:]
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-182:]
        buy_superorder_money = data['buy_superorder_money'].values[-182:]
        buy_smallorder_money = data['buy_smallorder_money'].values[-182:]
        sell_smallorder_count_v2 = data['sell_smallorder_count_v2'].values[-182:]
        weight = data['weight'].values[-182:]
        
        sbn_4_to_sun_w = np.nansum(sell_smallorder_count_v2 / replace_zero(SellUniqueOrderNum) * weight, axis=1)
        bba_4_to_ba_w = np.nansum(buy_smallorder_money / replace_zero(BuyTradeMoney) * weight, axis=1)
        bba_1 = np.nansum(buy_superorder_money, axis=1)
        
        factor = sbn_4_to_sun_w / bba_4_to_ba_w - auto_corr(bba_1, 80, 100)
        return factor[-1]