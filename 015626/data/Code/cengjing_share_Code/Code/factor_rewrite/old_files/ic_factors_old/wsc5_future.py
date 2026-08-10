import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *


class wsc5_future(FutureFactor):
    data_type = 'Future'
    days_past = 5
    data_dict = dict()
    instrument_type = 'recent'
    # data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low']}
    normalize_size = 1
    normalize_type = 'ts_rank'
    num_range = '(-0.5,1]'
    
    def calculate(self, data):
        future_close = data['close_cont_IC'].values[-1140:]
        future_high = data['high_cont_IC'].values[-1140:]
        future_low = data['low_cont_IC'].values[-1140:]
        N = 45
        bull_power = future_high - ts_truncated_ema(future_close, d=60, alpha=(N-1)/(N+1))
        bear_power = future_low - ts_truncated_ema(future_close, d=60, alpha=(N-1)/(N+1))
        factor_mean = -ts_mean(bull_power + bear_power, 180)
        factor_raw = ts_rank(factor_mean, 900)
        return factor_raw[-1]
