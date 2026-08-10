import numpy as np
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


class wsc_spot_2_if_IM(FutureFactor):
    """
    过去60分钟里，连续涨4分钟的bar的数量
    """
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000852.SH':['high']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        n = 4
        spot_high = data['high_000852.SH'].values[-66:]
        price_delta = (ts_delta(spot_high, 1) > 0).astype('int')
        factor_init = ts_sum(price_delta, n)
        factor_init[factor_init < 4] = 0
        factor = np.nanmean(factor_init[-60:])
        return factor