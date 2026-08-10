import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero


    
class wsc_hf_2_srch_if(FutureFactor):

    """
    搜索因子，factor_raw_1用主买独立成交订单数 / (主买独立成交订单数 + 主卖独立成交订单数)衡量当前时刻买卖压，
    factor_raw_2用主买独立订单数 / 主买订单数表征当前时刻单子金额大小
    在factor_raw_1和factor_raw_2量纲及分布相似的情况下对它们进行合成
    为了匹配因子库持仓时间，作ts_mean
    """
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'SellUniqueOrderNum', 'weight', 'BuyTradeNum']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy_unique_num = data['BuyUniqueOrderNum'].values[-21:]
        sell_unique_num = data['SellUniqueOrderNum'].values[-21:]
        buy_trade_num = data['BuyTradeNum'].values[-21:]
        stk_weight = data['weight'].values[-21:]
        
        factor_init_1 = np.nansum(buy_unique_num, axis=1)
        factor_init_2 = np.nansum(sell_unique_num, axis=1)

        factor_raw_1 = factor_init_1 / (factor_init_1 + factor_init_2)
        factor_raw_2 = np.nansum(buy_unique_num / replace_zero(buy_trade_num) * stk_weight, axis=1)
        factor_raw = factor_raw_2 + (ts_max(factor_raw_1, 16) + ts_min(factor_raw_1, 16)) / 2
        
        factor = -np.nanmean(factor_raw[-5:])
        return factor