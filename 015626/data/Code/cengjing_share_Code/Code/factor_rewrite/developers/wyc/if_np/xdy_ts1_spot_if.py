from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class xdy_ts1_spot_if(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close','high']}
    normalize_size = 5 * 242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '(-0.5,1]'
    handle_preadj = None 

    def calculate(self, df):
        high = df['high_000300.SH'][-80:].values
        close = df['close_000300.SH'][-80:].values
        high[abs(high) < 1e-8] = np.nan
        gain_high_30 = (high[30:] / high[:-30] - 1)[-20:]
        h_c = (close / high - 1)
        a = bk.move_mean(h_c, 60, 30, axis = 0)[-20:]
        a[abs(a) < 1e-8] = np.nan
        factor = bk.move_sum(gain_high_30 / a, 10, 5, axis = 0)[-10:]
        factor = np.nanmean(factor) * -1
        return factor