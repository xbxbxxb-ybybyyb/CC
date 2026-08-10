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

class wyc_ts29_icfuture_if(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close','volume']}
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '(-0.5,1]'
    handle_preadj = None 

    def calculate(self, df):
        close = df['close_cont_IC'][-1550:].values
        volume = df['volume_cont_IC'][-1530:].values
        
        factor = (close[20:] - close[:-20]) / close[:-20] * volume
        factor = bk.move_rank(factor, 300, 150, axis = 0)[-1230:]
        factor = bk.move_mean(factor, 20, 10, axis = 0)[-1210:]
        factor = get_norm(factor)

        return factor