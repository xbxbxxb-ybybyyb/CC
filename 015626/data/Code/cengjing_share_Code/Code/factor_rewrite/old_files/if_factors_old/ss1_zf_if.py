import pandas as pd
import numpy as np
import bottleneck as bk
from future_factor import FutureFactor

class ss1_zf_if(FutureFactor):
    '''
    期货类因子
    '''
    data_type = 'Future' #'IndexStock'
    days_past = 7
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close','high']}
    normalize_size = 242*5 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '[-0.5, 1]'

    def calculate(self, data):
        close = data['close_000300.SH'].iloc[-250*6-10:].values
        high = data['high_000300.SH'].iloc[-250*6-10:].values

        rtn = close[5:]/close[:-5]-1
        vol = bk.move_std(rtn, window = 250, min_count = 30)
        vol[vol<1e-8] = np.nan
        highmax = bk.move_max(high[:-5],window = 250, min_count = 30)
        ret = close[5:]/highmax -1       
        sig = ret/vol
        sig = bk.move_rank(sig, window = 242*5, min_count=242)
        return sig[-1]