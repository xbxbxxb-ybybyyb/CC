import numpy as np
import pandas as pd
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


class wsc_spot_11_if_IH(FutureFactor):
    """
    沪深300与上证50过去10分钟夏普比率之差
    """
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close'], '000016.SH':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        spot_close_if = data['close_000300.SH'].values[-42:]
        spot_close_ih = data['close_000016.SH'].values[-42:]
        
        n = 10
        spot_ret_if = ts_pct_change(spot_close_if, 1)
        spot_ret_ih = ts_pct_change(spot_close_ih, 1)
        sharpe_if = ts_mean(spot_ret_if, n) / ts_std(spot_ret_if, n)
        sharpe_ih = ts_mean(spot_ret_ih, n) / ts_std(spot_ret_ih, n)
        factor = np.nanmean((sharpe_if - sharpe_ih)[-30:])
        return factor
