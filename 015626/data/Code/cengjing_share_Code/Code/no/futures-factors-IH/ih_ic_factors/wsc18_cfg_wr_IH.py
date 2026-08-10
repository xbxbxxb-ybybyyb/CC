import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc18_cfg_wr_IH(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'open', 'high', 'low', 'weight', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '[-1,0.5)'
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-119:]
        stk_open = data['open_preadj'].values[-119:]
        stk_low = data['low_preadj'].values[-119:]
        stk_high = data['high_preadj'].values[-119:]
        stk_weight = data['weight'].values[-119:]
        weight_rank_mask = section_rank_np(stk_weight, pct=True) * 2 - 1
        n = 45
        a = abs(stk_high-ts_delay(stk_close, 1))
        b = abs(stk_low-ts_delay(stk_close, 1))
        c = abs(stk_high-ts_delay(stk_low, 1))
        d = abs(ts_delay(stk_close, 1)-ts_delay(stk_open, 1))
        k = np.maximum(a, b)
        m = ts_max(stk_high-stk_low, n)
        r1 = a + 0.5 * b + 0.25 * d
        r2 = b + 0.5 * a + 0.25 * d
        r3 = c + 0.25 * d
        r4 = np.where((a>=b)&(a>=c), r1, r2)
        r = np.where((c>=a)&(c>=b), r3, r4)
        si = 50 * (ts_delta(stk_close, 1) + ts_delay(stk_close, 1) - ts_delay(stk_open, 1) + 0.5*(stk_close - stk_open))\
            / replace_zero(r) * k / replace_zero(m)
        factor_raw = np.nansum(si * weight_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 70)
        return factor_mean[-1]
