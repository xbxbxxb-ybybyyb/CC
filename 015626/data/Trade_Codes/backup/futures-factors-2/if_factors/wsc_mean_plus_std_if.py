from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_mean_plus_std_if(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        spot_close = data['close_000905.SH'].values[-45:]
        spot_ret = ts_pct_change(spot_close, 5)
        ret_mean = ts_mean(spot_ret, 30)
        ret_std = ts_std(spot_ret, 30)
        factor_raw = ret_mean + 2 * ret_std
        factor_mean = ts_mean(factor_raw, 10)
        return factor_mean[-1]
