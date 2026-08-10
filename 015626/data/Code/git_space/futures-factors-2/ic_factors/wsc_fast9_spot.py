import numpy as np
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


class wsc_fast9_spot(FutureFactor):

    data_type = 'Future' 
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    
    def calculate(self, data):
        spot_close = data['close_000905.SH'].values[-64:]
        
        n = 10
        temp = replace_zero(ts_sum(abs(ts_delta(spot_close, 1)), n))
        vi = abs(ts_delta(spot_close, n)) / temp
        vidya = vi * spot_close + (1 - vi) * ts_delay(spot_close, 1)
        factor_raw = spot_close - vidya
        factor_mean = ts_mean(factor_raw, 50)
        return factor_mean[-1]