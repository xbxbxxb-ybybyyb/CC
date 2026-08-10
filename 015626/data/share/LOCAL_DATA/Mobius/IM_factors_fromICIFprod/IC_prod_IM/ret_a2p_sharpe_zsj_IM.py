import numpy as np
import numpy.ma as ma
import bottleneck as bk
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import *



class ret_a2p_sharpe_zsj_IM(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'close', 'adjfactor']
    normalize_size = 2400
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-42:]
        stk_close = data['close_preadj'].values[-42:]
        stk_ret = ts_pct_change(stk_close, 1)
        cut_line = np.nanmedian(stk_amount, axis=1, keepdims=True)
        active_raw = ma.array(stk_ret, mask=(stk_amount<cut_line))
        inactive_raw = ma.array(stk_ret, mask=(stk_amount>=cut_line))
        active_raw = np.nanmean(active_raw, axis=1)
        inactive_raw = np.nanmean(inactive_raw, axis=1)
        a = ts_std(active_raw, 10)
        b = ts_std(inactive_raw, 10)
        ret_active_sharpe_raw = ts_mean(active_raw, 10) / replace_zero(a)
        ret_inactive_sharpe_raw = ts_mean(inactive_raw, 10) / replace_zero(b)
        ret_a2p_sharpe_raw = ret_active_sharpe_raw - ret_inactive_sharpe_raw
        factor_raw = ts_mean(ret_a2p_sharpe_raw, 30)
        return factor_raw[-1]


