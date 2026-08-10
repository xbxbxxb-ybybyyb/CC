from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

def get_norm(fa):
    fmax = np.nanmax(fa)
    fmin = np.nanmin(fa)
    divisor = fmax - fmin
    if divisor < 1e-8:
        divisior = np.nan
    return ((fa[-1] - fmin)/ divisor) * 2 - 1

class wyc_ts49_future(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close']}
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 
    

    def calculate(self, df):
        close = df['close_cont_IC'][-1560:]
        csum = bk.move_sum(close, 100, 50, axis = 0) / 100
        con1 = ((csum[100:] - csum[:-100]) / close.shift(100)[100:]) <= 0.05
        
        temp1 = close[100:].copy(deep = True)
        temp1[con1] = close - bk.move_min(close, 200, 100, axis = 0)
        temp1[~con1] = close - close.shift(10)
        
        factor = bk.move_rank(temp1, 50, 25, axis = 0)[-1260:]
        factor = bk.move_mean(factor, 50, 25, axis = 0)[-1210:]
        factor = get_norm(factor)
        
        return factor
