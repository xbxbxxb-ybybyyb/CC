import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class bba_3_r_w_ic(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_midorder_money', 'sell_midorder_money_v2', 'weight']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy_midorder_money = data['buy_midorder_money'].values[-1]
        sell_midorder_money_v2 = data['sell_midorder_money_v2'].values[-1]
        weight = data['weight'].values[-1]

        factor = np.nansum(buy_midorder_money / replace_zero(buy_midorder_money + sell_midorder_money_v2) * weight)
        return factor