from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_search3_if(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['high']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        spot_high = data['high_000905.SH'].values[-75:]
        factor_raw = ts_std(spot_high, 75)
        return factor_raw[-1]
