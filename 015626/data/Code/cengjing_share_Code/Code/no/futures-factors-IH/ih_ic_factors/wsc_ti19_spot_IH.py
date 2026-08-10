from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero


class wsc_ti19_spot_IH(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000016.SH':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        spot_close = data['close_000016.SH'].values[-206:]
        temp = replace_zero(ts_sum(abs(ts_delta(spot_close, 1)), 10))
        vi = abs(ts_delta(spot_close, 10)) / temp
        vidya = vi * spot_close + (1 - vi) * ts_delay(spot_close, 1)
        factor_init = spot_close - vidya
        factor_raw = ts_mean(factor_init, 180)
        return factor_raw[-1]
