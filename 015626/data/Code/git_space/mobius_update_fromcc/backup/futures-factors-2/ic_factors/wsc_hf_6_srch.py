import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_6_srch(FutureFactor):
    # sba_4_to_sa * bbn_2_to_bun * ts_pred(sn, 30)
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_bigorder_count', 'BuyUniqueOrderNum', 'sell_smallorder_money_v2', 'SellTradeNum', 
                          'SellTradeMoney']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        SellTradeMoney = data['SellTradeMoney'].values[-32:]
        SellTradeNum = data['SellTradeNum'].values[-32:]
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-32:]
        buy_bigorder_count = data['buy_bigorder_count'].values[-32:]
        sell_smallorder_money_v2 = data['sell_smallorder_money_v2'].values[-32:]
        
        
        sba_4_to_sa = np.nansum(sell_smallorder_money_v2, axis=1) / replace_zero(np.nansum(SellTradeMoney, axis=1))
        bbn_2_to_bun = np.nansum(buy_bigorder_count, axis=1) / replace_zero(np.nansum(BuyUniqueOrderNum, axis=1))
        sn = np.nansum(SellTradeNum, axis=1)
        
        factor = sba_4_to_sa * bbn_2_to_bun * ts_pred(sn, 30)
        return factor[-1]