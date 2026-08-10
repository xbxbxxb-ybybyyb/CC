import numpy as np
from operators_wsc_1_0 import *
from future_factor import FutureFactor


class wsc_fast13_cfg_IH(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['amount', 'close', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        stk_close = data['close_preadj'].values[-7:]
        stk_amount = data['amount'].values[-7:]
        
        price_diff = ts_delta(stk_close, 1)
        up_num = (price_diff >= 0).sum(axis=1)
        down_num = (price_diff < 0).sum(axis=1)
        up_amount = np.nansum(np.where(price_diff >= 0, stk_amount, 0), axis=1)
        down_amount = np.nansum(np.where(price_diff < 0, stk_amount, 0), axis=1)
        factor_raw = (up_num / down_num) / (up_amount / down_amount)
        factor_mean = -ts_mean(factor_raw, 5)
        return factor_mean[-1]