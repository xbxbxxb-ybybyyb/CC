import numpy as np
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


class wsc_cfg_2_if(FutureFactor):
    """
    先对成分股计算过去30分钟里，连续涨4分钟的bar的数量减去连续跌4分钟的bar的数量，
    再用数量＞3根bar的权重之和减去数量<-3根bar(即连跌4分钟的bar比连涨4分钟的bar更多)的权重之和
    """
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['high', 'low', 'weight', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_high = data['high_preadj'].values[-36:]
        stk_low = data['low_preadj'].values[-36:]
        stk_weight = data['weight'].values[-1]
        
        n = 4
        m = 30
        price_delta1 = (ts_delta(stk_high, 1) > 0).astype('int')
        high_sum = ts_sum(price_delta1, n)
        high_sum[high_sum < n] = 0
        price_delta2 = (ts_delta(stk_low, 1) < 0).astype('int')
        low_sum = ts_sum(price_delta2, n)
        low_sum[low_sum < n] = 0
        factor_init = high_sum - low_sum
        factor_raw = ts_sum(factor_init, m)[-1]
        factor = stk_weight[factor_raw >= 3*n].sum() - stk_weight[factor_raw <= -3*n].sum()
        return factor