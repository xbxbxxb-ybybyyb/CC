import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *


class wsc8_cfg_as_if_IH(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'close', 'volume', 'adjfactor']
    normalize_size = 720
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-70:]
        stk_close = data['close_preadj'].values[-70:]
        stk_volume = data['volume_preadj'].values[-70:]
        factor_init = ts_cov(stk_close, stk_volume, 55)
        factor_raw = np.nansum(factor_init * stk_amount, axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        return factor_mean[-1]
