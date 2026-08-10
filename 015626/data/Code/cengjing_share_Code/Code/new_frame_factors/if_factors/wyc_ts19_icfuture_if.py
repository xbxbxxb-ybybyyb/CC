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

class wyc_ts19_icfuture_if(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close','high','low','volume']}
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 
    
    def calculate(self,df):
        close = df['close_cont_IC'][-1250:]
        high = df['high_cont_IC'][-1250:]
        low = df['low_cont_IC'][-1250:]
        volume = df['volume_cont_IC'][-1250:]
        
        a = high - low
        a[abs(a) < 1e-8] = np.nan
        factor = bk.move_sum(((close - low) - (high - close)) / a * volume, 20, 10, axis = 0)[-1230:]
        factor = bk.move_mean(factor, 30, 15, axis = 0)[-1200:]
        factor = get_norm(factor)
        return factor
    
