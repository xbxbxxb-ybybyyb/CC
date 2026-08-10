import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_28_srch(FutureFactor):
    # -min2(midprice(ts_skew(bba_2_r_w, 80), rolling_norm(ts_skew(bba_2_to_ba_w, 70), 115), 12), ts_rank(aroon(bun_r, sa_to_sun, 25), 90))
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_bigorder_money', 'sell_bigorder_money_v2', 'weight', 'BuyTradeMoney', 
                          'SellTradeMoney', 'BuyUniqueOrderNum', 'SellUniqueOrderNum']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy_bigorder_money = data['buy_bigorder_money'].values[-200:]
        sell_bigorder_money_v2 = data['sell_bigorder_money_v2'].values[-200:]
        weight = data['weight'].values[-200:]
        BuyTradeMoney = data['BuyTradeMoney'].values[-200:]
        SellTradeMoney = data['SellTradeMoney'].values[-200:]
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-200:]
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-200:]
        
        bba_2_r_w = np.nansum(buy_bigorder_money / replace_zero(buy_bigorder_money + sell_bigorder_money_v2) * weight, axis=1)
        bba_2_to_ba_w = np.nansum(buy_bigorder_money / replace_zero(BuyTradeMoney) * weight, axis=1)
        bun_r = np.nansum(BuyUniqueOrderNum, axis=1) / replace_zero(np.nansum(BuyUniqueOrderNum + SellUniqueOrderNum, axis=1))
        sa_to_sun = np.nansum(SellTradeMoney, axis=1) / replace_zero(np.nansum(SellUniqueOrderNum, axis=1))
        
        factor = min2(midprice(ts_skew(bba_2_r_w, 80), rolling_norm(ts_skew(bba_2_to_ba_w, 70), 115), 12), ts_rank(aroon(bun_r, sa_to_sun, 25), 90))
        return -factor[-1]