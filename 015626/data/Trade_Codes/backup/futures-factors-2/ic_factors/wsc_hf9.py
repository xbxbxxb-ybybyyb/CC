import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_inf



class wsc_hf9(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'weight', 'Bid1AmtMean', 'Ask1AmtMean']
    normalize_size = 500
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        stk_close = data['close'].values[-39:]
        stk_weight = data['weight'].values[-39:]
        stk_Bid1AmtMean = data['Bid1AmtMean'].values[-39:]
        stk_Ask1AmtMean = data['Ask1AmtMean'].values[-39:]
        stk_ret = replace_inf(ts_pct_change(stk_close, 20))
        flag1 = (stk_Bid1AmtMean >= stk_Ask1AmtMean)
        flag2 = (stk_ret >= 0)
        factor_init = np.nansum(ts_sum(flag1*flag2, 10)*stk_weight, axis=1)
        factor_raw = ts_mean(factor_init, 9)
        return factor_raw[-1]