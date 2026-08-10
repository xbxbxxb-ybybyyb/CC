import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

def ts_position(x, t):
    def get_position(ylist):
        smin = min(ylist)
        smax = max(ylist)
        y = ylist[-1]
        return (y - smin) / (smax - smin)
    return x.rolling(t, min_periods = t // 2).apply(get_position)

class xdy_ts4_spot(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['high']}
    normalize_size = 1210
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    handle_preadj = None 
    
    def calculate(self, df):
        high = df['high_000905.SH'][-130:]
        factor = ts_position(high, 30)
        factor = -1 * factor.rolling(100, min_periods=20).skew()
        return factor.values[-1]