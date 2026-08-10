import numpy as np
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


class wsc_spot_7_if(FutureFactor):
    """
    沪深300与中证500一分钟收益率之差
    """
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close'], '000905.SH':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        spot_close_if = data['close_000300.SH'].values[-11:]
        spot_close_ic = data['close_000905.SH'].values[-11:]
        factor_raw = ts_pct_change(spot_close_if, 1) - ts_pct_change(spot_close_ic, 1)
        factor = np.nanmean(factor_raw[-9:])
        return factor
