import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class ra_corr_if(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'amount', 'adjfactor']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        close = data['close_preadj'].iloc[-2:]
        amount = data['amount'].iloc[-1]

        factor = ts_pct_change(close, 1).iloc[-1].corr(amount)
        return factor