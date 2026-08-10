import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class bba_1_r_if(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_superorder_money', 'sell_superorder_money_v2']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy_superorder_money = data['buy_superorder_money'].values[-1]
        sell_superorder_money_v2 = data['sell_superorder_money_v2'].values[-1]

        factor = np.nansum(buy_superorder_money) / np.nansum(buy_superorder_money + sell_superorder_money_v2)
        return factor