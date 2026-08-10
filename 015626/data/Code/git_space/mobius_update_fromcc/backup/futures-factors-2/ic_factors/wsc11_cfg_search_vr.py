import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd
import datetime
 
class wsc11_cfg_search_vr(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close', 'adjfactor', 'stk_volatility']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        # mask
        volatility_mask = data['stk_volatility'][-15:]
        volatility_rank_mask = 2 * volatility_mask.rank(axis=1, pct=True).values - 1

        stk_close = data['close_preadj'][-50:].values
        stk_close_delta = stk_close[15:] - stk_close[:-15]
        factor_init = bk.move_max(stk_close_delta, 20, 10, axis = 0)

        factor_raw = np.nansum(factor_init[-15:] * volatility_rank_mask, axis=1)
        factor = np.nanmean(factor_raw)
     
        return factor