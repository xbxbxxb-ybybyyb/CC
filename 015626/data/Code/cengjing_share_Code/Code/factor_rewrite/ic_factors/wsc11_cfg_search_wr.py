import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc11_cfg_search_wr(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['weight', 'close', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-36:]
        stk_weight = data['weight'].iloc[-36:]
        weight_rank_mask = stk_weight.rank(axis=1, pct=True) * 2 - 1
        # weight_rank_mask = section_rank_np(stk_weight, pct=True) * 2 - 1
        factor_init = ts_max(ts_delta(stk_close, 15), 20)
        factor_raw = np.nansum(factor_init * weight_rank_mask.values, axis=1)
        return factor_raw[-1]
