import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc11_future_IM(FutureFactor):
    data_type = 'Future'
    days_past = 6
    data_dict = dict()
    instrument_type = 'recent'
    # data_dict['Index_Id'] = {'000852.SH':['close']}
    data_dict['Index_Id'] = {'000852.SH':['close', 'high', 'low', 'open']}
    normalize_size = 1
    normalize_type = 'ts_rank'
#    num_range = '(-0.5,1]'
    
    def calculate(self, data):
        future_close = data['close_000852.SH'].values[-1314:]
        future_high = data['high_000852.SH'].values[-1314:]
        future_low = data['low_000852.SH'].values[-1314:]
        future_open = data['open_000852.SH'].values[-1314:]
        n = 20
        a = abs(future_high-ts_delay(future_close, 1))
        b = abs(future_low-ts_delay(future_close, 1))
        c = abs(future_high-ts_delay(future_low, 1))
        d = abs(ts_delay(future_close, 1)-ts_delay(future_open, 1))
        k = np.maximum(a, b)
        m = ts_max(future_high-future_low, n)
        r1 = a + 0.5 * b + 0.25 * d
        r2 = b + 0.5 * a + 0.25 * d
        r3 = c + 0.25 * d
        r4 = np.where((a>=b)&(a>=c), r1, r2)
        r = np.where((c>=a)&(c>=b), r3, r4)
        si = 50 * (ts_delta(future_close, 1) + ts_delay(future_close, 1) - ts_delay(future_open, 1)\
                   + 0.5*(future_close - future_open)) / r * k / m
        factor_mean = ts_mean(si, 90)
        factor_raw = ts_rank(factor_mean, 1200)
        return factor_raw[-1]
