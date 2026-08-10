import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_27_srch_modified_if(FutureFactor):
    # -add2(bun_to_bn_w, mul2(bun_to_bn_w, min2(bbn_4_to_bun, midprice(bba_4_r, auto_corr(bba_1_to_ba_w, 90, 70), 10))))
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'BuyTradeNum', 'weight', 'buy_smallorder_count', 
                          'buy_smallorder_money', 'sell_smallorder_money_v2', 'buy_superorder_money', 
                          'BuyTradeMoney']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-170:]
        BuyTradeNum = data['BuyTradeNum'].values[-170:]
        weight = data['weight'].values[-170:]
        buy_smallorder_count = data['buy_smallorder_count'].values[-170:]
        buy_smallorder_money = data['buy_smallorder_money'].values[-170:]
        sell_smallorder_money_v2 = data['sell_smallorder_money_v2'].values[-170:]
        buy_superorder_money = data['buy_superorder_money'].values[-170:]
        BuyTradeMoney = data['BuyTradeMoney'].values[-170:]
        
        bun_to_bn_w = np.nansum(BuyUniqueOrderNum / replace_zero(BuyTradeNum) * weight, axis=1)
        bbn_4_to_bun = np.nansum(buy_smallorder_count, axis=1) / replace_zero(np.nansum(BuyUniqueOrderNum, axis=1))
        bba_4_r = np.nansum(buy_smallorder_money, axis=1) / replace_zero(np.nansum(buy_smallorder_money + sell_smallorder_money_v2, axis=1))
        bba_1_to_ba_w = np.nansum(buy_superorder_money / replace_zero(BuyTradeMoney) * weight, axis=1)
        
        factor = -add2(bun_to_bn_w, mul2(bun_to_bn_w, min2(bbn_4_to_bun, midprice(bba_4_r, auto_corr(bba_1_to_ba_w, 90, 70), 10))))
        return factor[-1]