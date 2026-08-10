import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_30_srch(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['sell_small_lo_amount', 'sell_lo_amount', 'buy_bigorder_money', 'BuyTradeMoney', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        sell_small_lo_amount = data['sell_small_lo_amount'].values[-35:]
        sell_lo_amount = data['sell_lo_amount'].values[-35:]
        buy_bigorder_money = data['buy_bigorder_money'].values[-35:]
        BuyTradeMoney = data['BuyTradeMoney'].values[-35:]
        weight = data['weight'].values[-35:]
        
        bosa_4_to_osa = np.nansum(sell_small_lo_amount, axis=1) / replace_zero(np.nansum(sell_lo_amount, axis=1))
        bba_2_to_ba_w = np.nansum(buy_bigorder_money / replace_zero(BuyTradeMoney) * weight, axis=1)
        factor = midprice(bosa_4_to_osa, bbands_down(bba_2_to_ba_w, 20), 10)[-1]
        
        return factor