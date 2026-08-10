import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_cfg3(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'weight', 'adjfactor']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-70:]
        stk_weight = data['weight'].values[-70:]
        spot_close = data['close_000905.SH'].values[-70:]
        stk_ret = ts_pct_change(stk_close, 60)
        index_ret = ts_pct_change(spot_close, 60)
        # print(index_ret)
        excess_ret = sub2(stk_ret, index_ret)
        # print(excess_ret)
        excess_ret[excess_ret>=0] = 0
        excess_ret[excess_ret<0] = 1
        #print(excess_ret.shape)
        factor_raw = np.nansum(excess_ret * stk_weight, axis=1)
        factor_raw = ts_mean(factor_raw, 10)
        #print(factor_raw.shape)
        return factor_raw[-1]