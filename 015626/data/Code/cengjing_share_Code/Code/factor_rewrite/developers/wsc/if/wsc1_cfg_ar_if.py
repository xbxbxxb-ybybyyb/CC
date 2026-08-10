import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc1_cfg_ar_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Index_Id'] = {'000300.SH':['close']}
    data_dict['Stock'] = ['amount', 'close']
    normalize_size = 600
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-76:]
        stk_close = data['close_preadj'].values[-76:]
        spot_close = data['close_000300.SH'].values[-76:]
        amount_rank_mask = section_rank_np(stk_amount, pct=True) * 2 - 1
        stk_ret = ts_pct_change(stk_close, 60)
        spot_ret = ts_pct_change(spot_close, 60)
        excess_ret = stk_ret - spot_ret
        amount_rank_mask[np.isnan(excess_ret)] = np.nan
        amount_rank_mask[excess_ret >= 0] = np.nan
        factor_raw = -np.nanmean(amount_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        return factor_mean[-1]
