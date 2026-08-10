import numpy as np
import pandas as pd
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


class wsc_spot_10_if(FutureFactor):
    """
    沪深300指数处于历史波动率高位（75%分位数）的分钟的收益率
    """
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        spot_close = data['close_000300.SH'].iloc[-167:]
        
        spot_ret_if = ts_pct_change(spot_close, 1)
        ret_std_if = ts_std(spot_ret_if, 15)
        std_up = (ret_std_if > ret_std_if.rolling(30, min_periods=15).quantile(0.75)) + 0.
        factor_raw = spot_ret_if * std_up
        factor = np.nanmean(factor_raw[-120:])
        return factor
