import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd
import datetime
 
class wsc_cfg7(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close', 'adjfactor', 'weight']
    normalize_size = 500 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        # 长短期收益率之差
        stk_close = data['close_preadj'][-121:]
        stk_ret_short = stk_close.pct_change(15, fill_method=None)
        stk_ret_long = stk_close.pct_change(120, fill_method=None) 
        a = stk_ret_long - stk_ret_short
        a[a<0] = 0
        factor = np.nansum((a[-1:] * data['weight'][-1:]).values,axis = 1)      
        return factor