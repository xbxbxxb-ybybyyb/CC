import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *


class wsc5_cfg_ar_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'close']
    normalize_size = 240
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-100:]
        stk_close = data['close_preadj'].values[-100:]
        amount_rank_mask = section_rank_np(stk_amount, pct=True) * 2 - 1
        ma_long = ts_mean(stk_close, 90)
        ma_short = ts_mean(stk_close, 15)
        ma_diff = ma_short - ma_long
        factor_raw = np.nansum(ma_diff * amount_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 10)
        return factor_mean[-1]
