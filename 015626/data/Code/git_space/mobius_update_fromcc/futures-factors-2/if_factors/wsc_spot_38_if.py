import numpy as np
import pandas as pd
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


class wsc_spot_38_if(FutureFactor):
    # 最近一段时间收益率MSE * 当前分钟涨跌方向，即带方向的波动

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        spot_close_if = data['close_000300.SH'].values[-42:]
        
        factor_raw = np.sign(ts_pct_change(spot_close_if, 1)) * ts_sum((ts_pct_change(spot_close_if, 1) ** 2), 10)
        factor = np.nanmean(factor_raw[-30:])
        return factor