import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_23_srch_modified_if(FutureFactor):
    # -add2(auto_corr(ba_to_bn_w, 100, 100), square(add2(long_short_ma_ratio(bba_1_to_ba_w, 90, 45), div2(square(midpoint(bba_4_r, 20)), sba_4_to_sa))))
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeMoney', 'BuyTradeNum', 'weight', 'buy_superorder_money', 
                          'buy_smallorder_money', 'sell_smallorder_money_v2', 'SellTradeMoney']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        BuyTradeMoney = data['BuyTradeMoney'].values[-200:]
        BuyTradeNum = data['BuyTradeNum'].values[-200:]
        weight = data['weight'].values[-200:]
        buy_superorder_money = data['buy_superorder_money'].values[-200:]
        buy_smallorder_money = data['buy_smallorder_money'].values[-200:]
        sell_smallorder_money_v2 = data['sell_smallorder_money_v2'].values[-200:]
        SellTradeMoney = data['SellTradeMoney'].values[-200:]
        
        ba_to_bn_w = np.nansum(BuyTradeMoney / replace_zero(BuyTradeNum) * weight, axis=1)
        bba_1_to_ba_w = np.nansum(buy_superorder_money / replace_zero(BuyTradeMoney) * weight, axis=1)
        bba_4_r = np.nansum(buy_smallorder_money, axis=1) / replace_zero(np.nansum(buy_smallorder_money + sell_smallorder_money_v2, axis=1))
        sba_4_to_sa = np.nansum(sell_smallorder_money_v2, axis=1) / replace_zero(np.nansum(SellTradeMoney, axis=1))
        
        factor = -add2(auto_corr(ba_to_bn_w, 100, 100), square(add2(long_short_ma_ratio(bba_1_to_ba_w, 90, 45), div2(square(midpoint(bba_4_r, 20)), sba_4_to_sa))))
        return factor[-1]