import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_10_srch(FutureFactor):
    # sba_4_to_sa * ts_decay_linear(ts_argmax(sun, 20), 72)
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['SellTradeMoney', 'BuyUniqueOrderNum', 'SellUniqueOrderNum', 'sell_smallorder_money_v2']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        SellTradeMoney = data['SellTradeMoney'].values[-95:]
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-95:]
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-95:]
        sell_smallorder_money_v2 = data['sell_smallorder_money_v2'].values[-95:]
        
        sba_4_to_sa = np.nansum(sell_smallorder_money_v2, axis=1) / replace_zero(np.nansum(SellTradeMoney, axis=1))
        sun = np.nansum(SellUniqueOrderNum, axis=1)
        factor = sba_4_to_sa * ts_decay_linear(ts_argmax(sun, 20), 72)
        return factor[-1]