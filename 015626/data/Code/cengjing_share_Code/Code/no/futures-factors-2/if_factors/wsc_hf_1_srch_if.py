import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero


    
class wsc_hf_1_srch_if(FutureFactor):

    """
    -midpoint(bun_r, 10)
    factor_raw用主买独立成交订单数 / (主买独立成交订单数 + 主卖独立成交订单数)衡量当前时刻买卖压，
    再对factor_raw求过去10分钟的最大值与最小值，将它们相加
    """
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'SellUniqueOrderNum']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy_unique_num = data['BuyUniqueOrderNum'].values[-7:]
        sell_unique_num = data['SellUniqueOrderNum'].values[-7:]
        
        factor_init_1 = np.nansum(buy_unique_num, axis=1)
        factor_init_2 = np.nansum(sell_unique_num, axis=1)
        
        factor_raw = -factor_init_1 / (factor_init_1 + factor_init_2)
        factor = np.nanmax(factor_raw) + np.nanmin(factor_raw)
        return factor