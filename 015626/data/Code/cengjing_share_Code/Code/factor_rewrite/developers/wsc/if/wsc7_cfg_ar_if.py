import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc7_cfg_ar_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'close']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-71:]
        stk_close = data['close_preadj'].values[-71:]
        amount_rank_mask = section_rank_np(stk_amount, pct=True) * 2 - 1
        stk_ret = ts_pct_change(stk_close, 5)
        b = ts_mean(stk_ret, 30)
        c = ts_std(stk_ret, 30)
        factor_init = 3 * b + c
        factor_raw = np.nansum(factor_init * amount_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 35)
        return factor_mean[-1]
