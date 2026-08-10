from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd
import scipy

class xdy_ts4_spot_if(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['high']}
    normalize_size = 5 * 242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 
    
    def calculate(self, df):
        high = df['high_000300.SH'][-105:].values
        fmax = bk.move_max(high, 30, 15, axis = 0)
        fmin = bk.move_min(high, 30, 15, axis = 0)
        a = fmax - fmin
        a[a<1e-8] = np.nan
        factor = ((high - fmin) / a)[-75:]
        
        factor = -1 * scipy.stats.skew(factor, bias = False)

        return factor