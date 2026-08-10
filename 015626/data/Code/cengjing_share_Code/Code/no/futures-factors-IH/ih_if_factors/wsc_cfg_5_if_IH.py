import numpy as np
import pandas as pd
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


class wsc_cfg_5_if_IH(FutureFactor):
    """
    沪深300成分股的一分钟收益率按等权和按成分股权重加权得到的结果之差
    """
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'weight', 'adjfactor']
    normalize_size = 500
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-15:]
        stk_weight = data['weight'].values[-15:]
        
        stk_ret = ts_pct_change(stk_close, 1)
        ret_ew = np.nanmean(stk_ret, axis=1)
        ret_w = np.nansum(stk_ret * stk_weight, axis=1)
        factor = np.nanmean((ret_w - ret_ew)[-13:])
        return factor