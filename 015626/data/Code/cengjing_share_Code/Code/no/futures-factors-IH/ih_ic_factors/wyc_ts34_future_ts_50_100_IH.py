from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_ts34_future_ts_50_100_IH(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 2
    data_dict = dict()
    data_dict['Stock'] = ['close', 'turnover_rate', 'high', 'low', 'volume', 'adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[0,1]'
    handle_preadj = True 

    def calculate(self, df):
        high = df['high_preadj'][-300:].values
        low = df['low_preadj'][-300:].values
        close = df['close_preadj'][-300:].values
        volume = df['volume_preadj'][-300:].values
        chl = high - low
        chl[abs(chl) < 1e-6] = np.nan
        factor = ((close - low)-(high - close))/ chl * volume
        factor = bk.move_mean(factor, 150, 75, axis = 0)[-150:]

        t = df['turnover_rate'][-150:].values
        factor = factor * t
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 50, 25, axis = 0)[-100:]
        factor = np.nanmean(factor)
        return factor