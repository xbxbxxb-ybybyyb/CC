import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_11_srch(FutureFactor):
    # sba_4_to_sa * ts_pred(bbands_down(bbn_2_to_bun_w, 60), 100)
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['SellTradeMoney', 'BuyUniqueOrderNum', 'buy_bigorder_money', 
                          'sell_smallorder_money_v2', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        SellTradeMoney = data['SellTradeMoney'].values[-162:]
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-162:]
        buy_bigorder_money = data['buy_bigorder_money'].values[-162:]
        sell_smallorder_money_v2 = data['sell_smallorder_money_v2'].values[-162:]
        weight = data['weight'].values[-162:]
        
        sba_4_to_sa = np.nansum(sell_smallorder_money_v2, axis=1) / replace_zero(np.nansum(SellTradeMoney, axis=1))
        bbn_2_to_bun_w = np.nansum(buy_bigorder_money / replace_zero(BuyUniqueOrderNum) * weight, axis=1)
        factor = sba_4_to_sa * ts_pred(bbands_down(bbn_2_to_bun_w, 60), 100)
        return factor[-1]