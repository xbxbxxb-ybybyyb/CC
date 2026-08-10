import pandas as pd
import numpy as np
import bottleneck as bk
from future_factor import FutureFactor

class rt1_zf_if_IH(FutureFactor):
    '''
    期货类因子
    '''
    data_type = 'Future' #'IndexStock'
    days_past = 3
    data_dict = dict()
    data_dict['Index_Id'] = {'000016.SH':['close','low']}
    normalize_size = 0 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'

    def calculate(self, data):
        close = data['close_000016.SH'].iloc[-242*2-71:].values
        low = data['low_000016.SH'].iloc[-242*2-71:].values
        lowmin = bk.move_min(low, window = 60, min_count = 30)
        sig = close/lowmin
        sig = bk.move_rank(sig, window = 242*2, min_count = 242)
        sig = np.nanmean(sig[-10:])
        return sig

