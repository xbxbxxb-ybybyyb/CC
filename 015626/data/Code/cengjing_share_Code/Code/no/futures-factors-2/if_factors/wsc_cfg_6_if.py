import numpy as np
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


class wsc_cfg_6_if(FutureFactor):
    """
    成分股权重前50%股票的过去40分钟平均收益率减去权重前50%股票的过去40分钟平均收益率
    """

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'weight', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        stk_close = data['close_preadj'].values[-41:]
        stk_weight = data['weight'].values[-1]
        
        stk_ret = ts_pct_change(stk_close, 1)
        factor_init = np.nansum(stk_ret[-40:], axis=0)
        factor = np.nanmean(factor_init[stk_weight > np.nanmedian(stk_weight)]) - np.nanmean(factor_init[stk_weight < np.nanmedian(stk_weight)])
        return factor