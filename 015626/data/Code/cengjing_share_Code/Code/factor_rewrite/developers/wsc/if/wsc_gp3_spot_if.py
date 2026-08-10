from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_gp3_spot_if(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['low']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        spot_low = data['low_000300.SH'].values[-260:]
        factor_raw = ts_median(ts_delta(ts_pct_change(spot_low, 120), 115), 25)
        return factor_raw[-1]