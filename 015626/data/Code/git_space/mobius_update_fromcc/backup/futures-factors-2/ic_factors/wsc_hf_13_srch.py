import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_13_srch(FutureFactor):
    # -(bba_4_r / bn_r + midpoint(bba_4_r, 20))
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeNum', 'SellTradeNum', 'buy_smallorder_money', 'sell_smallorder_money_v2']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        BuyTradeNum = data['BuyTradeNum'].values[-20:]
        SellTradeNum = data['SellTradeNum'].values[-20:]
        buy_smallorder_money = data['buy_smallorder_money'].values[-20:]
        sell_smallorder_money_v2 = data['sell_smallorder_money_v2'].values[-20:]
        
        bba_4_r = np.nansum(buy_smallorder_money, axis=1) / (np.nansum(buy_smallorder_money, axis=1) + np.nansum(sell_smallorder_money_v2, axis=1))
        bn_r = np.nansum(BuyTradeNum, axis=1) / (np.nansum(BuyTradeNum, axis=1) + np.nansum(SellTradeNum, axis=1))
        
        factor = -(bba_4_r / bn_r + midpoint(bba_4_r, 20))
        return factor[-1]