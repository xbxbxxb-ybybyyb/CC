import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

def get_norm(fa):
    fmax = np.nanmax(fa)
    fmin = np.nanmin(fa)
    divisor = fmax - fmin
    if divisor < 1e-8:
        divisior = np.nan
    return ((fa[-1] - fmin)/ divisor) * 2 - 1

class wyc_ts25_future(FutureFactor):

    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close']}
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    handle_preadj = None 
    
    def calculate(self, df):
        c = df['close_cont_IC'][-1310:].values
        factor =  bk.move_mean(c, 20, min_count=10, axis = 0) / c
        factor = (bk.move_rank(factor[-1290:], 20, min_count=10, axis = 0) + 1)/2
        factor = bk.move_mean(factor[-1270:], 60, min_count=30, axis = 0)[-1210:]
        factor = get_norm(factor)
        return factor