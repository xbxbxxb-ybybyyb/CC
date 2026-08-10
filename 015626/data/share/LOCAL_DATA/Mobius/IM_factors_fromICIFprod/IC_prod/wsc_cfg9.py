import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import multi_processing_joblib
from operators_wsc_1_0 import *


class wsc_cfg9(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'weight', 'high', 'low', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'rolling_norm'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-125:]
        stk_high = data['high_preadj'].values[-125:]
        stk_low = data['low_preadj'].values[-125:]
        stk_weight = data['weight'].values[-125:]
        N = 30
        stk_close_ema = multi_processing_joblib(stk_close, ts_truncated_ema, n_jobs=-1, d=60, alpha=(N-1)/(N+1))
        bull_power = stk_high - stk_close_ema
        bear_power = stk_low - stk_close_ema
        factor_init = bull_power + bear_power
        factor_raw = np.nansum(factor_init * stk_weight, axis=1)
        factor_raw = -ts_mean(factor_raw, 65)
        return factor_raw[-1]
