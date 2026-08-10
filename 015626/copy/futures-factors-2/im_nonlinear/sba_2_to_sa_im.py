import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class sba_2_to_sa_im(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['sell_bigorder_money_v2', 'SellTradeMoney']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        sell_bigorder_money_v2 = data['sell_bigorder_money_v2'].values[-1]
        SellTradeMoney = data['SellTradeMoney'].values[-1]

        factor = np.nansum(sell_bigorder_money_v2) / np.nansum(SellTradeMoney)
        return factor