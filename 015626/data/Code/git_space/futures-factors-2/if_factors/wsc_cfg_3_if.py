import numpy as np
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


class wsc_cfg_3_if(FutureFactor):
    """
    过去120分钟卡玛比率最小的12.5%的股票的权重之和，权重越小因子值越大
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
        stk_close = data['close_preadj'].iloc[-122:]
        stk_weight = data['weight'].values[-1]
        
        n = 120
        stk_ret = ts_pct_change(stk_close, 1).iloc[-n:]
        x = stk_ret.cumsum()
        y = x - x.expanding().max()
        factor_mdd = y.min().values
        factor_ret = -np.nansum(stk_ret.values, axis=0)
        factor_init = factor_ret / replace_zero(factor_mdd)
        factor = -stk_weight[factor_init < np.nanquantile(factor_init, 0.125)].mean()
        return factor