import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc13_cfg_ar(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'volume', 'adjfactor']
    normalize_size = 2000
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-55:]
        stk_volume = data['volume_preadj'].values[-55:]
        amount_rank_mask = section_rank_np(stk_amount, pct=True) * 2 - 1
        stk_vwap = stk_amount / replace_zero(stk_volume)
        vwap_ma = ts_mean(stk_vwap, 45)
        amount_ma = ts_mean(stk_amount, 45)
        volume_ma = replace_zero(ts_mean(stk_volume, 45))
        temp = replace_zero(amount_ma / volume_ma)
        apb = vwap_ma / temp
        factor_init = -np.log(apb)
        factor_raw = np.nansum(factor_init * amount_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 10)
        return factor_mean[-1]