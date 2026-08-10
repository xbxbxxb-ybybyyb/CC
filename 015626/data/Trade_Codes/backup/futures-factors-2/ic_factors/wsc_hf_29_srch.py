import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_29_srch(FutureFactor):
    # -(aroon(ts_argmin(ra_corr, 90), sbn_3_to_sun, 30) + aroon(bun_to_bn_w, midpoint(bun_r, 20), 60))
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['sell_midorder_count_v2', 'SellUniqueOrderNum', 'weight', 'BuyUniqueOrderNum', 
                          'BuyTradeNum', 'close', 'amount']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        sell_midorder_count_v2 = data['sell_midorder_count_v2'].values[-121:]
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-121:]
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-121:]
        BuyTradeNum = data['BuyTradeNum'].values[-121:]
        weight = data['weight'].values[-121:]
        close = data['close'].iloc[-121:]
        amount = data['amount'].iloc[-121:]
        
        ra_corr = ts_pct_change(close, 1).corrwith(amount, axis=1).values
        sbn_3_to_sun = np.nansum(sell_midorder_count_v2, axis=1) / replace_zero(np.nansum(SellUniqueOrderNum, axis=1))
        bun_to_bn_w = np.nansum(BuyUniqueOrderNum / replace_zero(BuyTradeNum) * weight, axis=1)
        bun_r = np.nansum(BuyUniqueOrderNum, axis=1) / replace_zero(np.nansum(BuyUniqueOrderNum + SellUniqueOrderNum, axis=1))
                
        factor = aroon(ts_argmin(ra_corr, 90), sbn_3_to_sun, 30) + aroon(bun_to_bn_w, midpoint(bun_r, 20), 60)
        return -factor[-1]