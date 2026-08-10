import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc11_cfg_vs_if_IH(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['stk_volatility', 'close', 'high', 'low', 'adjfactor']
    normalize_size = 480
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_volatility = data['stk_volatility'].values[-220:]
        stk_close = data['close_preadj'].values[-220:]
        stk_high = data['high_preadj'].values[-220:]
        stk_low = data['low_preadj'].values[-220:]
        n = 30
        m = 150
        low_n = ts_min(stk_low, n)
        high_n = ts_max(stk_high, n)
        a = high_n - low_n
        stochastics = (stk_close- low_n) / replace_zero(a)
        stochastics_low = ts_min(stochastics, m)
        stochastics_high = ts_max(stochastics, m)
        c = stochastics_high - stochastics_low
        stochastics_double = (stochastics - stochastics_low) / replace_zero(c)
        factor_raw = np.nansum(stochastics_double * stk_volatility, axis=1)
        factor_mean = ts_mean(factor_raw, 40)
        return factor_mean[-1]
