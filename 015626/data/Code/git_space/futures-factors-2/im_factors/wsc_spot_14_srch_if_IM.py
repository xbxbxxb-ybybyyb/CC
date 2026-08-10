import numpy as np
import pandas as pd
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


class wsc_spot_14_srch_if_IM(FutureFactor):
    """
    -ts_decay_linear(ts_skew(spot_close, 10), 20)
    """
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Index_Id'] = {'000852.SH':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        spot_close = data['close_000852.SH'].iloc[-30:]
        
        factor = -ts_decay_linear(ts_skew(spot_close, 10), 20)
        return factor[-1]
