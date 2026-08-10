import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc2_cfg_cr_IH(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'stk_index_corr_sh50', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '(-0.9,1]'
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-48:]
        stk_index_corr = data['stk_index_corr_sh50'].values[-48:]
        corr_rank_mask  = 2 * section_rank_np(stk_index_corr, pct=True) - 1
        stk_ret = ts_pct_change(stk_close, 3)
        ret_mean_plus_std = ts_mean(stk_ret, 30) + 0.5 * ts_std(stk_ret, 30)
        factor_init = np.nansum(ret_mean_plus_std * corr_rank_mask, axis=1)
        factor_raw = ts_mean(factor_init, 15)
        return factor_raw[-1]