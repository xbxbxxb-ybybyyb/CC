import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class tp_abs_to_c_w_ic(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['abs_px_path_tran', 'close', 'weight']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        abs_px_path_tran = data['abs_px_path_tran'].values[-1]
        close = data['close'].values[-1]
        weight = data['weight'].values[-1]

        factor = np.nansum(abs_px_path_tran / replace_zero(close) * weight)
        return factor