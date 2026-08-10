import numpy as np
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


class wsc_spot_1_if_IM(FutureFactor):
    """
    过去10分钟的上行波动率比下行波动率
    """
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000852.SH':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        n = 10
        spot_close = data['close_000852.SH'].values[-12:]
        sbj_ret = ts_pct_change(spot_close, 1)
        sbj_ret_up = sbj_ret.copy()
        sbj_ret_up[sbj_ret_up < 0] = 0
        sbj_ret_down = sbj_ret.copy()
        sbj_ret_down[sbj_ret_down > 0] = 0
        factor_raw = ts_std(sbj_ret_up, n) / ts_std(sbj_ret_down, n)        
        return -factor_raw[-1]
