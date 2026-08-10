import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_14_srch(FutureFactor):
    # -bba_4_r_w / ba_r_w * (midprice(bba_4_r, auto_corr(bba_1_to_ba_w, 90, 90), 10) + bba_4_to_ba)
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeMoney', 'SellTradeMoney', 'buy_superorder_money', 'buy_smallorder_money', 
                          'sell_smallorder_money_v2', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        BuyTradeMoney = data['BuyTradeMoney'].values[-200:]
        SellTradeMoney = data['SellTradeMoney'].values[-200:]
        buy_superorder_money = data['buy_superorder_money'].values[-200:]
        buy_smallorder_money = data['buy_smallorder_money'].values[-200:]
        sell_smallorder_money_v2 = data['sell_smallorder_money_v2'].values[-200:]
        weight = data['weight'].values[-200:]
        
        bba_4_r_w = np.nansum(buy_smallorder_money / replace_zero(buy_smallorder_money + sell_smallorder_money_v2) * weight, axis=1)
        ba_r_w = np.nansum(BuyTradeMoney / replace_zero(BuyTradeMoney + SellTradeMoney) * weight, axis=1)
        bba_4_r = np.nansum(buy_smallorder_money, axis=1) / (np.nansum(buy_smallorder_money, axis=1) + np.nansum(sell_smallorder_money_v2, axis=1))
        bba_1_to_ba_w = np.nansum(buy_superorder_money / replace_zero(BuyTradeMoney) * weight, axis=1)
        bba_4_to_ba = np.nansum(buy_smallorder_money, axis=1) / replace_zero(np.nansum(BuyTradeMoney, axis=1))
        
        factor = -bba_4_r_w / ba_r_w * (midprice(bba_4_r, auto_corr(bba_1_to_ba_w, 90, 90), 10) + bba_4_to_ba)
        return factor[-1]