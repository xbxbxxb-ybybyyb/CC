from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_1_spot_if(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close', 'volume']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        spot_close = data['close_000300.SH'].values[-138:]
        spot_volume = data['volume_000300.SH'].values[-138:]
        spot_ret = ts_pct_change(spot_close, 1)
        log_ret = log(spot_ret+1)
        ret_std = ts_std(spot_ret, 15)
        log_ret_weight = log_ret / spot_volume * ret_std
        factor_raw = ts_sum(log_ret_weight, 120)
        return factor_raw[-1]
