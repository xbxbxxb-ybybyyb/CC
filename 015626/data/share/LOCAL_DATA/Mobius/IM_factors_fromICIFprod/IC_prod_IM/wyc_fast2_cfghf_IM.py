import numpy as np
from operators_wsc_1_0 import *
from future_factor import FutureFactor



class wyc_fast2_cfghf_IM(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['amount', 'close', 'BuyUniqueOrderNum', 'SellUniqueOrderNum']
    normalize_size = 237 * 3
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False

    def calculate(self, data):
        stk_close = data['close'].values[-12:]
        stk_amount = data['amount'].values[-12:]
        stk_BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-12:]
        stk_SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-12:]
        
        order_num = stk_BuyUniqueOrderNum + stk_SellUniqueOrderNum
        ret = ts_pct_change(stk_close, 1)
        ret[ret > 0] = 0
        ret[ret < 0] = 1
        down_amount = stk_amount * ret
        down_ordernum = order_num * ret
        amount_per_order = ts_sum(np.nansum(stk_amount, axis=1), 10) / ts_sum(np.nansum(order_num, axis=1), 10)
        down_amount_per_order = ts_sum(np.nansum(down_amount, axis=1), 10) / ts_sum(np.nansum(down_ordernum, axis=1), 10)
        factor = amount_per_order / down_amount_per_order
        return factor[-1]