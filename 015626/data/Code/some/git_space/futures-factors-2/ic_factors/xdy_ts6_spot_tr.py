from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

        
class xdy_ts6_spot_tr(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 2
    data_dict = dict()
    data_dict['Stock'] = ['close','turnover_rate','adjfactor']
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[-1,0.2]'
    handle_preadj = True
    
    def calculate(self, df):
        close = df['close_preadj'][-365:].values
        gain_close_30 = close[30:]/close[:-30] - 1
        factor = 2 * gain_close_30[20:] - gain_close_30[:-20]
        factor = bk.move_mean(factor, 110, 55, axis = 0)[-205:]
       
        t = df['turnover_rate'][-205:]
        tr = (2 * t.rank(axis=1, pct=True) - 1).values
        factor = factor * tr
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 200, 100, axis = 0)[-5:]
        factor = np.nanmean(factor)

        return factor
