import numpy as np
import pandas as pd
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


class wsc_spot_13_if(FutureFactor):
    """
    沪深300高收益率部分波动率与低收益率部分波动率的关系，收益率高低用是否大于ts_median衡量
    """
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        spot_close = data['close_000300.SH'].iloc[-38:]
        spot_ret = ts_pct_change(spot_close, 1)
        
        n = 18
        ret_median = ts_median(spot_ret, n)
        up_ret = spot_ret.copy()
        up_ret[up_ret<ret_median] = np.nan
        down_ret = spot_ret.copy()
        down_ret[down_ret>ret_median] = np.nan
        factor = (up_ret.rolling(n, min_periods=5).std() - down_ret.rolling(n, min_periods=5).std()) / \
                     (up_ret.rolling(n, min_periods=5).std() + down_ret.rolling(n, min_periods=5).std())
        return -factor[-1]
