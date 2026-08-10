import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

class wyc_ts102_spot(FutureFactor):

    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close','volume']}
    normalize_size = 1210
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    handle_preadj = None 
    
    def calculate(self, df):
        v = df['volume_000300.SH'][-17:].values
        c = df['close_000300.SH'][-17:].values
        v_delta = v[5:] - v[:-5]
        c_delta = c[5:] - c[:-5]
        a = -1 * np.sign(v_delta) * c_delta
        factor = bk.move_mean(a, 2, min_count=1, axis= 0)[-10:]
        factor = np.nanmean(factor)
        return factor