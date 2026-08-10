from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_search6_long_if(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['open']}
    normalize_size = 600
    normalize_type = 'rolling_norm'
#    num_range = '(-0.5,1]'
    
    def calculate(self, data):
        spot_open = data['open_000905.SH'].values[-50:]
        factor_raw = ts_median(ts_delta(spot_open, 20), 30)
        return factor_raw[-1]
