import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc1_cfg_vr(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'stk_volatility', 'adjfactor']
    normalize_size = 900
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-80:]
        volatility_mask = data['stk_volatility'].values[-80:]
        volatility_rank_mask = 2 * section_rank_np(volatility_mask, pct=True) - 1
        close_ma_long = ts_mean(stk_close, 75)
        close_ma_short = ts_mean(stk_close, 10)
        close_ma_diff = close_ma_short - close_ma_long
        factor_init = np.nansum(close_ma_diff * volatility_rank_mask, axis=1)
        factor_raw = ts_mean(factor_init, 5)
        return factor_raw[-1]

