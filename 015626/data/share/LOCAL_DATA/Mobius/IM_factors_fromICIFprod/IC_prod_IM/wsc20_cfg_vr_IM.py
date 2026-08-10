import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc20_cfg_vr_IM(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Index_Id'] = {'000852.SH':['close']}
    data_dict['Stock'] = ['close', 'stk_volatility', 'adjfactor']
    normalize_size = 2400
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-60:]
        spot_close = data['close_000852.SH'].values[-60:]
        stk_volatility = data['stk_volatility'].values[-60:]
        stk_volatility_rank_mask = section_rank_np(stk_volatility, pct=True) * 2 - 1
        stk_ret = ts_pct_change(stk_close, 45)
        spot_ret = ts_pct_change(spot_close, 45)
        excess_ret = stk_ret - spot_ret
        stk_volatility_rank_mask[np.isnan(excess_ret)] = np.nan
        stk_volatility_rank_mask[excess_ret >= 0] = 0
        factor_raw = np.nansum(stk_volatility_rank_mask, axis=1)
        factor_mean = -ts_mean(factor_raw, 15)
        return factor_mean[-1]
