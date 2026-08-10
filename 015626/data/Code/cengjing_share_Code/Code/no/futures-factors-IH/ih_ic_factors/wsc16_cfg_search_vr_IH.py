import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc16_cfg_search_vr_IH(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'stk_volatility', 'adjfactor']
    normalize_size = 1800
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-35:]
        stk_volatility = data['stk_volatility'].values[-35:]
        stk_volatility_rank_mask = section_rank_np(stk_volatility, pct=True) * 2 - 1 
        factor_init = ts_reg_beta(stk_close, 15)
        factor_raw = np.nansum(factor_init * stk_volatility_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 20)
        return factor_mean[-1]
