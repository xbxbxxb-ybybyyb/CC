from future_factor import FutureFactor
from operators_wsc_1_0 import *


class wsc3_future_if_IM(FutureFactor):
    data_type = 'Future'
    days_past = 6
    data_dict = dict()
    instrument_type = 'recent'
    # data_dict['Index_Id'] = {'000852.SH':['close']}
    data_dict['Index_Id'] = {'000852.SH':['close']}
    normalize_size = 1
    normalize_type = 'ts_rank'
#    num_range = '(-0.5,1]'
    
    def calculate(self, data):
        future_close = data['close_000852.SH'].values[-1240:]
        future_ret = ts_pct_change(future_close, 5)
        ret_mean = ts_mean(future_ret, 24)
        ret_std = ts_std(future_ret, 24)
        factor_init = ret_mean + 2 * ret_std
        factor_raw = ts_mean(factor_init, 10)
        factor_mean = ts_rank(factor_raw, 1200)
        return factor_mean[-1]
