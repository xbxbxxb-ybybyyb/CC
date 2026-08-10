import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_16_srch(FutureFactor):
    # -ts_distance_from_mean(bba_4_r - bn_r + midprice(bba_4_r, coefficient_of_variation(bbn_1_to_bun_w, 50), 10) + bba_4_to_ba, 110)
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_smallorder_money', 'sell_smallorder_money_v2', 'BuyTradeNum', 'SellTradeNum', 
                          'buy_superorder_count', 'BuyUniqueOrderNum', 'BuyTradeMoney', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy_smallorder_money = data['buy_smallorder_money'].values[-170:]
        sell_smallorder_money_v2 = data['sell_smallorder_money_v2'].values[-170:]
        BuyTradeNum = data['BuyTradeNum'].values[-170:]
        SellTradeNum = data['SellTradeNum'].values[-170:]
        buy_superorder_count = data['buy_superorder_count'].values[-170:]
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-170:]
        BuyTradeMoney = data['BuyTradeMoney'].values[-170:]        
        weight = data['weight'].values[-170:]
        
        bba_4_r = np.nansum(buy_smallorder_money, axis=1) / np.nansum(buy_smallorder_money + sell_smallorder_money_v2, axis=1)
        bn_r = np.nansum(BuyTradeNum, axis=1) / np.nansum(BuyTradeNum + SellTradeNum, axis=1)
        bbn_1_to_bun_w = np.nansum(buy_superorder_count / replace_zero(BuyUniqueOrderNum) * weight, axis=1)
        bba_4_to_ba = np.nansum(buy_smallorder_money, axis=1) / np.nansum(BuyTradeMoney, axis=1)
        
        factor = -ts_distance_from_mean(bba_4_r - bn_r + midprice(bba_4_r, coefficient_of_variation(bbn_1_to_bun_w, 50), 10) + bba_4_to_ba, 110)
        return factor[-1]