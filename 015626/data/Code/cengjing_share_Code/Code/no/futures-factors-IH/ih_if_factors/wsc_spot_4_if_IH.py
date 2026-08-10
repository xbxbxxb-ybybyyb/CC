import numpy as np
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


class wsc_spot_4_if_IH(FutureFactor):
    """
    对过去1/5/10/15/20分钟的平均收益率进行比较
    """
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000016.SH':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        spot_close = data['close_000016.SH'].values[-36:]
        x1 = ts_pct_change(spot_close, 1) / 1
        x2 = ts_pct_change(spot_close, 5) / 5
        x3 = ts_pct_change(spot_close, 10) / 10
        x4 = ts_pct_change(spot_close, 15) / 15
        x5 = ts_pct_change(spot_close, 20) / 20
        factor_raw = ((x1 > x2) + 0.) + ((x2 > x3) + 0.) + ((x3 > x4) + 0.) + ((x4 > x5) + 0.)
        factor = -np.nanmean(factor_raw[-15:])
        return factor
