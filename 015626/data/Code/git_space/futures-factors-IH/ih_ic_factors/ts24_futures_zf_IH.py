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

class ts24_futures_zf_IH(FutureFactor):

    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IH':['close','high','low']} 
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    handle_preadj = None 
    
    def calculate(self, data):
        N = 20
        wmadf = bk.move_mean(data['close_cont_IH'][-1350:].values, N, min_count=N//2, axis = 0)
        longc = bk.move_max(data['high_cont_IH'][-1350:].values, N, min_count=N//2, axis = 0) - wmadf
        shortc = bk.move_min(data['low_cont_IH'][-1350:].values, N, min_count=N//2) - wmadf
        factor =  ((longc - shortc) / data['close_cont_IH'][-1350:].values)[-1330:]
        factor = bk.move_rank(factor, 80, min_count=40, axis = 0)[-1250:]
        factor = bk.move_mean(factor, 40, min_count=20, axis = 0)[-1210:]
        factor = get_norm(factor)
        return factor