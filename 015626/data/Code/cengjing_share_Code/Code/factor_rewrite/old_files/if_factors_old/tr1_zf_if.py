import pandas as pd
import numpy as np
import bottleneck as bk
from future_factor import FutureFactor

class tr1_zf_if(FutureFactor):
    '''
    期货类因子
    '''
    data_type = 'Future' #'IndexStock'
    days_past = 2
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close','high','low']}
    normalize_size = 242*3 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '(-0.5, 1]'

    def calculate(self, data):
        close = data['close_000300.SH'].iloc[-1]
        high = data['high_000300.SH'].iloc[-121*2-1:].values
        low = data['low_000300.SH'].iloc[-121*2-1:].values
        hh = np.nanmax(high[-121*2:])
        ll = np.nanmin(low[-121*2:])
        hhll = hh+ll
        if abs(hhll) < 1e-8:
            hhll = np.nan
        return 2*close/hhll