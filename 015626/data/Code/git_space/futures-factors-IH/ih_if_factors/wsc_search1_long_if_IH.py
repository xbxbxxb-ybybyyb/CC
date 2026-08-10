from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_search1_long_if_IH(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000016.SH':['close']}
    normalize_size = 1000
    normalize_type = 'rolling_norm'
#    num_range = '(-0.5,1]'
    
    def calculate(self, data):
        spot_close = data['close_000016.SH'].values[-40:]
        factor_raw = ts_reg_beta(spot_close, 40)
        return factor_raw[-1]

