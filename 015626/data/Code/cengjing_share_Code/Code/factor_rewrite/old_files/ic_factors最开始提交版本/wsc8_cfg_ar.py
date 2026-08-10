import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc8_cfg_ar(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'high', 'low', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_high = data['high_preadj'].values[-42:]
        stk_low = data['low_preadj'].values[-42:]
        stk_amount = data['amount'].values[-42:]
        amount_rank_mask = section_rank_np(stk_amount, pct=True) * 2 - 1
        n = 30
        hl = stk_high + stk_low
        high_abs = abs(ts_delta(stk_high, 1))
        low_abs = abs(ts_delta(stk_low, 1))
        dmz = np.maximum(high_abs, low_abs)
        dmz[ts_delta(hl, 1)<=0] = 0
        dmf = np.maximum(high_abs, low_abs)
        dmf[ts_delta(hl, 1)>=0] = 0
        a = replace_zero(ts_sum(dmz, n) + ts_sum(dmf, n))
        ddi = (ts_sum(dmz, n) - ts_sum(dmf, n)) / a
        factor_raw = np.nansum(ddi * amount_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 10)
        return factor_mean[-1]
