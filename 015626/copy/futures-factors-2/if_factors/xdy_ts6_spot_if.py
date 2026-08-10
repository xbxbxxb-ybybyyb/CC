from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class xdy_ts6_spot_if(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 5*242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None
    
    def calculate(self, df):
        close = df['close_000300.SH'][-185:].values
        gain_close_15 = close[15:]/close[:-15] - 1
        factor = 2 * gain_close_15[20:] - gain_close_15[:-20]
        factor = np.nanmean(factor)
        return factor