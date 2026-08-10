import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc20_cfg_cr_IH(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Index_Id'] = {'000016.SH':['close']}
    data_dict['Stock'] = ['close', 'stk_index_corr_sh50', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '[0,1]'
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-70:]
        spot_close = data['close_000016.SH'].values[-70:]
        stk_index_corr = data['stk_index_corr_sh50'].values[-70:]
        stk_index_corr_rank_mask = section_rank_np(stk_index_corr, pct=True) * 2 - 1
        stk_ret = ts_pct_change(stk_close, 45)
        spot_ret = ts_pct_change(spot_close, 45)
        excess_ret = stk_ret - spot_ret
        stk_index_corr_rank_mask[np.isnan(excess_ret)] = np.nan
        stk_index_corr_rank_mask[excess_ret >= 0] = 0
        factor_raw = np.nansum(stk_index_corr_rank_mask, axis=1)
        factor_mean = -ts_mean(factor_raw, 25)
        return factor_mean[-1]
