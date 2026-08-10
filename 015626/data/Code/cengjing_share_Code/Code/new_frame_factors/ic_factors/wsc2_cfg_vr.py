import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd
import datetime
 
class wsc2_cfg_vr(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close', 'adjfactor', 'stk_volatility']
    normalize_size = 1800 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        # mask
        volatility_mask = data['stk_volatility'][-16:]
        volatility_rank_mask = 2 * volatility_mask.rank(axis=1, pct=True).values - 1
            
        # as follows
        a = data['close_preadj'][-50:].values
        a = a[3:] / a[:-3] - 1
        b = bk.move_mean(a, 30, 15, axis = 0)
        c = bk.move_std(a, 30, 15, axis = 0)
        factor_init = 4 * b + c
        factor_raw = np.nansum(factor_init[-16:] * volatility_rank_mask[-16:], axis=1)
        factor = np.nanmean(factor_raw)
     
        return factor