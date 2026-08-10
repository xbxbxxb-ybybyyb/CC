from future_factor import FutureFactor
from operators_wsc_1_0 import *


class wsc_mean_plus_std_IH(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000016.SH':['close']}
    normalize_size = 600
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        spot_close = data['close_000016.SH'].values[-45:]
        spot_ret = ts_pct_change(spot_close, 5)
        close_mean = ts_mean(spot_ret, 30)
        close_std = ts_std(spot_ret, 30)
        factor_init = close_mean + 2 * close_std
        factor_raw = ts_mean(factor_init, 10)
        return factor_raw[-1]
