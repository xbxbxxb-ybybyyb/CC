import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd
import scipy

class stk2indx_skew_zsj(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close','adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        ##### def data #####
        stk_close = data['close_preadj'][-26:]
        stk_ret = stk_close / stk_close.shift(1) - 1
        stk2indx_skew_raw = stk_ret.skew(axis=1).values
        ma = bk.move_mean(stk2indx_skew_raw,5,2,axis = 0)[-20:]
        factor = np.nanmean(ma)
        return factor