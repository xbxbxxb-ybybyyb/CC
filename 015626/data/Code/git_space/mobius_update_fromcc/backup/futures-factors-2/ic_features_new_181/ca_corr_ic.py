import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class ca_corr_ic(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'amount', 'adjfactor']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        close = data['close_preadj'].iloc[-1]
        amount = data['amount'].iloc[-1]

        factor = close.corr(amount)
        return factor