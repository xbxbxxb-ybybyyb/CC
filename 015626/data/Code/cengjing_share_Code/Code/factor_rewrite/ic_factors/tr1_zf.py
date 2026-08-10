import pandas as pd
import numpy as np
import bottleneck as bk
from future_factor import FutureFactor

class tr1_zf(FutureFactor):
    '''
    期货类因子
    '''
    data_type = 'Future' #'IndexStock'
    days_past = 2
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close','low','high']}
    normalize_size = 242 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'

    def calculate(self, data):
        high = data['high_000905.SH'].values
        high = high[-242:]
        hh = np.nanmax(high)
        low = data['low_000905.SH'].values
        low = low[-242:]
        ll = np.nanmin(low)
        return (2*data['close_000905.SH'].values[-1])/(hh+ll)