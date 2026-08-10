import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_24_srch(FutureFactor):
    # -(bba_4_to_ba_w + midprice(bba_4_r, ts_skew(bba_2_to_ba_w, 60), 10) + bun_to_bn)
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_smallorder_money', 'BuyTradeMoney', 'weight', 'sell_smallorder_money_v2',
                          'buy_bigorder_money', 'BuyUniqueOrderNum', 'BuyTradeNum']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy_smallorder_money = data['buy_smallorder_money'].values[-70:]
        BuyTradeMoney = data['BuyTradeMoney'].values[-70:]
        weight = data['weight'].values[-70:]
        sell_smallorder_money_v2 = data['sell_smallorder_money_v2'].values[-70:]
        buy_bigorder_money = data['buy_bigorder_money'].values[-70:]
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-70:]
        BuyTradeNum = data['BuyTradeNum'].values[-70:]
        
        bba_4_to_ba_w = np.nansum(buy_smallorder_money / replace_zero(BuyTradeMoney) * weight, axis=1)
        bba_4_r = np.nansum(buy_smallorder_money, axis=1) / replace_zero(np.nansum(buy_smallorder_money + sell_smallorder_money_v2, axis=1))
        bba_2_to_ba_w = np.nansum(buy_bigorder_money / replace_zero(BuyTradeMoney) * weight, axis=1)
        bun_to_bn = np.nansum(BuyUniqueOrderNum, axis=1) / replace_zero(np.nansum(BuyTradeNum, axis=1))
        
        factor = bba_4_to_ba_w + midprice(bba_4_r, ts_skew(bba_2_to_ba_w, 60), 10) + bun_to_bn
        return -factor[-1]