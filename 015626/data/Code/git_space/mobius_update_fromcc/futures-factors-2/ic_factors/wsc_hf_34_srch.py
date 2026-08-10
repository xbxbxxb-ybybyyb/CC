import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_34_srch(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'amount', 'adjfactor', 'sell_midorder_count_v2', 'SellUniqueOrderNum', 'BuyUniqueOrderNum', 'BuyTradeNum', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        
        close = data['close_preadj'].iloc[-125:]
        amount = data['amount'].iloc[-125:]
        sell_midorder_count_v2 = data['sell_midorder_count_v2'].values[-125:]
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-125:]
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-125:]
        BuyTradeNum = data['BuyTradeNum'].values[-125:]
        weight = data['weight'].values[-125:]
             
        ra_corr = ts_pct_change(close, 1).corrwith(amount, axis=1).values
        sbn_3_to_sun = np.nansum(sell_midorder_count_v2, axis=1) / replace_zero(np.nansum(SellUniqueOrderNum, axis=1))
        bun_to_bn_w = np.nansum(BuyUniqueOrderNum / replace_zero(BuyTradeNum) * weight, axis=1)
        bun_r = np.nansum(BuyUniqueOrderNum, axis=1) / np.nansum(BuyUniqueOrderNum + SellUniqueOrderNum, axis=1)
        
        factor = -add2(aroon(ts_argmin(ra_corr, 90), sbn_3_to_sun, 30), aroon(bun_to_bn_w, midpoint(bun_r, 20), 60))[-1]
        
        return factor