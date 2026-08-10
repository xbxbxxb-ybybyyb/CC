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

class wyc_ts225_future(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IH':['close']}
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 
    
    def calculate(self, df):
        cih = df['close_cont_IH'][-1310:].values
        cih[abs(cih) < 1e-8] = np.nan
        factor = bk.move_mean(cih, 20, 10, axis = 0)[-1290:] / cih[-1290:]
        factor = bk.move_rank(factor, 20, 10, axis = 0)[-1270:]
        factor = bk.move_mean(factor, 60, 30, axis = 0)[-1210:]
        factor = get_norm(factor)
        
        return factor