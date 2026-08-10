from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_ts20_icspot_if_IH(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 5
    data_dict = dict()
    data_dict['Index_Id'] = {'000016.SH':['close','high','low','volume']}
    normalize_size = 4 * 242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 

    def calculate(self, df):
        close = df['close_000016.SH'][-1008:]
        high = df['high_000016.SH'][-1008:]
        low = df['low_000016.SH'][-1008:]
        volume = df['volume_000016.SH'][-1008:]
        
        a = high - low
        a[abs(a) < 1e-8] = np.nan
        factor = bk.move_sum(((close - low) - (high - close)) / a * volume, 20, 10, axis = 0)[-988:]
        
        factor = bk.move_rank(factor, 968, 484, axis = 0)[-20:]
        factor = np.nanmean(factor)
        
        return factor
