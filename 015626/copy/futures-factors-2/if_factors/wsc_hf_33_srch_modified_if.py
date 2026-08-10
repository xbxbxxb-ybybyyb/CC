import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_33_srch_modified_if(FutureFactor):
    # -midprice(ts_skew(bn_r, 15), ts_sum(bba_4_to_ba_w, 15), 5)
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeNum', 'SellTradeNum', 'buy_smallorder_money', 'BuyTradeMoney', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        BuyTradeNum = data['BuyTradeNum'].values[-20:]
        SellTradeNum = data['SellTradeNum'].values[-20:]
        buy_smallorder_money = data['buy_smallorder_money'].values[-20:]
        BuyTradeMoney = data['BuyTradeMoney'].values[-20:]
        weight = data['weight'].values[-20:]
        
        bn_r = np.nansum(BuyTradeNum, axis=1) / replace_zero(np.nansum(BuyTradeNum + SellTradeNum, axis=1))
        bba_4_to_ba_w = np.nansum(buy_smallorder_money / replace_zero(BuyTradeMoney) * weight, axis=1)
        
        factor = -midprice(ts_skew(bn_r, 15), ts_sum(bba_4_to_ba_w, 15), 5)
        return factor[-1]