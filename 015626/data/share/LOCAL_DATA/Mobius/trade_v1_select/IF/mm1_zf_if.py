import pandas as pd
import numpy as np
import bottleneck as bk
from future_factor import FutureFactor

class mm1_zf_if(FutureFactor):
    '''
    期货类因子
    '''
    data_type = 'Future' #'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 0 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'

    def calculate(self, data):
        close = data['close_000300.SH'].iloc[-85:].values
        close_max = bk.move_max(close,window = 60, min_count = 30)
        close_min = bk.move_min(close, window = 60, min_count = 30)
        tmp = close_max - close_min
        tmp[abs(tmp)<1e-8] = np.nan
        close_norm = (close-close_min)/tmp*2-1
        return np.nanmean(close_norm[-20:])