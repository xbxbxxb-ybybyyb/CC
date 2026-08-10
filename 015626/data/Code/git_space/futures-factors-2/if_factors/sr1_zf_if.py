import pandas as pd
import numpy as np
import bottleneck as bk
from future_factor import FutureFactor

class sr1_zf_if(FutureFactor):
    '''
    期货类因子
    '''
    data_type = 'Future' #'IndexStock'
    days_past = 3
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close','low']}
    normalize_size = 0 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'

    def calculate(self, data):
        close = data['close_000300.SH'].iloc[-242*2-70:].values
        low = data['low_000300.SH'].iloc[-242*2-70:].values

        rtn = close[1:]/close[:-1]-1
        vol = bk.move_std(rtn, window = 60, min_count = 30)
        vol[vol<1e-8] = np.nan
        lowmin = bk.move_min(low[:-1],window = 60, min_count = 30)
        ret = close[1:]/lowmin -1       
        sig = ret/vol
        sig = bk.move_rank(sig, window = 242*2, min_count=242)
        sig = np.nanmean(sig[-5:])
        return sig