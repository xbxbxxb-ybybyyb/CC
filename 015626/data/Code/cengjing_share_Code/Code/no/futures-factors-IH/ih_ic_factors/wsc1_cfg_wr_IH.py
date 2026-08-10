import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *


class wsc1_cfg_wr_IH(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'weight', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-90:]
        stk_weight = data['weight'].values[-90:]
        weight_rank_mask = 2 * section_rank_np(stk_weight, pct=True) - 1
        close_ma_long = ts_mean(stk_close, 90)
        close_ma_short = ts_mean(stk_close, 15)
        close_ma_diff = close_ma_short - close_ma_long
        factor_raw = np.nansum(close_ma_diff[-1] * weight_rank_mask[-1])
        return factor_raw
