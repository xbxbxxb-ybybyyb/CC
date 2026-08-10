import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_22_srch_modified_if(FutureFactor):
    # -add2(bun_to_bn_w, midprice(mul2(ts_skew(sn, 60), mul2(bba_4_to_ba_w, bun_r_w)), bba_4_r, 10))
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'BuyTradeNum', 'weight', 'SellTradeNum', 'buy_smallorder_money', 
                          'BuyTradeMoney', 'sell_smallorder_money_v2', 'SellUniqueOrderNum']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-70:]
        BuyTradeNum = data['BuyTradeNum'].values[-70:]
        weight = data['weight'].values[-70:]
        SellTradeNum = data['SellTradeNum'].values[-70:]
        buy_smallorder_money = data['buy_smallorder_money'].values[-70:]
        sell_smallorder_money_v2 = data['sell_smallorder_money_v2'].values[-70:]
        BuyTradeMoney = data['BuyTradeMoney'].values[-70:]
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-70:]
        
        bun_to_bn_w = np.nansum(BuyUniqueOrderNum / replace_zero(BuyTradeNum) * weight, axis=1)
        sn = np.nansum(SellTradeNum, axis=1)
        bba_4_to_ba_w = np.nansum(buy_smallorder_money / replace_zero(BuyTradeMoney) * weight, axis=1)
        bun_r_w = np.nansum(BuyUniqueOrderNum / replace_zero(BuyUniqueOrderNum + SellUniqueOrderNum) * weight, axis=1)
        bba_4_r = np.nansum(buy_smallorder_money, axis=1) / replace_zero(np.nansum(buy_smallorder_money + sell_smallorder_money_v2, axis=1))
        
        factor = -add2(bun_to_bn_w, midprice(mul2(ts_skew(sn, 60), mul2(bba_4_to_ba_w, bun_r_w)), bba_4_r, 10))
        return factor[-1]