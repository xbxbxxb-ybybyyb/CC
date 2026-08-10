import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc20_cfg_vs(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Stock'] = ['close', 'stk_volatility', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '[-1,0]'
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-60:]
        spot_close = data['close_000905.SH'].values[-60:]
        stk_volatility = data['stk_volatility'].values[-60:]
        stk_ret = ts_pct_change(stk_close, 45)
        spot_ret = ts_pct_change(spot_close, 45)
        excess_ret = stk_ret - spot_ret
        stk_volatility[np.isnan(excess_ret)] = np.nan
        stk_volatility[excess_ret >= 0] = 0
        factor_raw = np.nansum(stk_volatility, axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        return factor_mean[-1]
