import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc11_cfg_search_cr(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['stk_index_corr_zz500', 'close', 'adjfactor']
    normalize_size = 1800
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-46:]
        stk_index_corr_zz500 = data['stk_index_corr_zz500'].values[-46:]
        stk_index_corr_rank_mask = section_rank_np(stk_index_corr_zz500, pct=True) * 2 - 1
        factor_init = ts_max(ts_delta(stk_close, 15), 15)
        factor_raw = np.nansum(factor_init * stk_index_corr_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        return factor_mean[-1]
