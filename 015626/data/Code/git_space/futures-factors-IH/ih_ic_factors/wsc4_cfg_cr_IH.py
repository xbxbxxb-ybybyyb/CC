import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc4_cfg_cr_IH(FutureFactor):
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
        stk_close = data['close_preadj'].values[-47:]
        stk_index_corr = data['stk_index_corr_sh50'].values[-47:]
        stk_index_corr_rank_mask = 2 * section_rank_np(stk_index_corr, pct=True) - 1
        N = 20
        dpo = stk_close - ts_delay(ts_mean(stk_close, N), int(N/2+1))
        factor_raw = np.nansum(dpo * stk_index_corr_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        return factor_mean[-1]
