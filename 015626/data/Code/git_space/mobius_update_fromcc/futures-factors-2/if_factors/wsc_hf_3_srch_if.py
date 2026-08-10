import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero


        
class wsc_hf_3_srch_if(FutureFactor):

    """
    搜索因子，factor_raw用主买成交订单数 / (主买成交订单数 + 主卖成交订单数)衡量当前时刻买卖压
    """
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeNum', 'SellTradeNum']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy_trade_num = data['BuyTradeNum'].values[-25:]
        sell_trade_num = data['SellTradeNum'].values[-25:]
        
        factor_init_1 = np.nansum(buy_trade_num, axis=1)
        factor_init_2 = np.nansum(sell_trade_num, axis=1)

        factor_raw = factor_init_1 / (factor_init_1 + factor_init_2)        
        factor = ts_min(ts_mean(factor_raw, 15) - factor_raw, 10)
        return factor[-1]