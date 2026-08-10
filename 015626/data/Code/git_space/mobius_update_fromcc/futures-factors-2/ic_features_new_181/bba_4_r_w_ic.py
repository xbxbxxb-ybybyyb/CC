import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class bba_4_r_w_ic(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_smallorder_money', 'sell_smallorder_money_v2', 'weight']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy_smallorder_money = data['buy_smallorder_money'].values[-1]
        sell_smallorder_money_v2 = data['sell_smallorder_money_v2'].values[-1]
        weight = data['weight'].values[-1]

        factor = np.nansum(buy_smallorder_money / replace_zero(buy_smallorder_money + sell_smallorder_money_v2) * weight)
        return factor