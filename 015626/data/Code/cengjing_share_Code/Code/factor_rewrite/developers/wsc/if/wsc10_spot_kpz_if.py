import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc10_spot_kpz_if(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = '(-0.5,1]'
    
    def calculate(self, data):
        spot_close = data['close_000905.SH'].values[-94:]
        spot_high = data['high_000905.SH'].values[-94:]
        spot_low = data['low_000905.SH'].values[-94:]
        n = 30
        hl = spot_high + spot_low
        high_abs = abs(ts_delta(spot_high, 1))
        low_abs = abs(ts_delta(spot_low, 1))
        dmz = np.maximum(high_abs, low_abs)
        dmz[ts_delta(hl, 1)<=0] = 0
        dmf = np.maximum(high_abs, low_abs)
        dmf[ts_delta(hl, 1)>=0] = 0
        a = ts_sum(dmz, n) + ts_sum(dmf, n)
        ddi = (ts_sum(dmz, n) - ts_sum(dmf, n)) / replace_zero(a)
        factor_raw = ts_mean(ddi, 60)
        return factor_raw[-1]
