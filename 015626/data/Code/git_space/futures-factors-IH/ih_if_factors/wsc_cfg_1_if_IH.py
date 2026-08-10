import numpy as np
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


class wsc_cfg_1_if_IH(FutureFactor):
    """
    过去45分钟夏普比率最大的10%的股票的权重之和减去夏普比率最小的10%的股票的权重之和
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
        stk_close = data['close_preadj'].values[-47:]
        stk_weight = data['weight'].values[-1]
        
        n = 45
        sbj_ret = ts_pct_change(stk_close, 1)
        factor_sharpe = ts_mean(sbj_ret, n) / ts_std(sbj_ret, n)
        factor_sharpe = factor_sharpe[-1]
        factor = stk_weight[factor_sharpe > np.nanquantile(factor_sharpe, 0.9)].mean() - stk_weight[factor_sharpe < np.nanquantile(factor_sharpe, 0.1)].mean()
        return factor