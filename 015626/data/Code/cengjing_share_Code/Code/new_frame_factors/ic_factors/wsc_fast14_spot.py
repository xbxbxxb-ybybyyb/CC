import numpy as np
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


class wsc_fast14_spot(FutureFactor):

    data_type = 'Future' 
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'amount']}
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    
    def calculate(self, data):
        spot_close = data['close_000905.SH'].values[-20:]
        spot_high = data['high_000905.SH'].values[-20:]
        spot_low = data['low_000905.SH'].values[-20:]
        spot_amount = data['amount_000905.SH'].values[-20:]
        
        factor_raw = (2 * spot_close - spot_high - spot_low) / replace_zero(spot_high - spot_low) * spot_amount
        factor_mean = ts_mean(factor_raw, 20)
        return factor_mean[-1]