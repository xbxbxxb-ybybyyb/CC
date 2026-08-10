import numpy as np
import numpy.ma as ma
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_42_if(FutureFactor):
    # 挂单买卖压和他过去3天同时刻的值之比

    data_type = 'IndexStock' 
    days_past = 4
    data_dict = dict()
    data_dict['Stock'] = ['buy_lo_amount', 'sell_lo_amount']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy_lo_amount = data['buy_lo_amount'].values
        sell_lo_amount = data['sell_lo_amount'].values
        
        factor_init = np.nansum(buy_lo_amount, axis=1) / replace_zero(
            np.nansum(buy_lo_amount + sell_lo_amount, axis=1))
        factor_raw = (factor_init[-237:] / np.nanmean(factor_init[-237*3:].reshape(3, 237), axis=0))[-60:]
        factor = np.nanmean(factor_raw)
        return factor