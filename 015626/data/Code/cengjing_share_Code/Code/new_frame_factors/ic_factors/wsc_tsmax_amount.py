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

class wsc_tsmax_amount(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['amount']}
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    handle_preadj = None 
    
    def calculate(self, df):
        factor = df['amount_cont_IC'][-165:].values
        factor = bk.move_max(factor, 45, min_count=22, axis = 0)[-120:]
        factor = get_norm(factor)
        return factor