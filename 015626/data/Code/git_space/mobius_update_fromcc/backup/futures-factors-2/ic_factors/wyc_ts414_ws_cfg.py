import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd
import datetime
 
class wyc_ts414_ws_cfg(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close', 'adjfactor', 'weight']
    normalize_size = 5 * 242 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, df):
        c = df['close_preadj'][-32:].values
        s = df['close_preadj'].rolling(30, min_periods = 15).std()[-32:].values
        
        factor = np.where(c[2:] > c[:-2], s[2:], 0)

        factor = factor[-30:] * df['weight'][-30:].values
        factor = np.nansum(factor, axis = 1)[-30:]
        factor = np.nanmean(factor)
      
        return factor