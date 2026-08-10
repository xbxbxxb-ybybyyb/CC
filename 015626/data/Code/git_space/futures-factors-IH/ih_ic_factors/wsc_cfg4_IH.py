import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_cfg4_IH(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'weight', 'high', 'low', 'open', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-65:]
        stk_open = data['open_preadj'].values[-65:]
        stk_high = data['high_preadj'].values[-65:]
        stk_low = data['low_preadj'].values[-65:]
        stk_weight = data['weight'].values[-65:]
        a = stk_high - stk_low
        a[a<1e-5] = np.nan
        b = stk_close - stk_open
        b[b<0] = np.nan
        c = ts_sum(b/a, 60)
        factor_raw = np.nansum(c * stk_weight, axis=1)
        factor_raw = ts_mean(factor_raw, 5)
        return factor_raw[-1]