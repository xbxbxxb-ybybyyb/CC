from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_ts44_future_ws(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 2
    data_dict = dict()
    data_dict['Stock'] = ['close', 'volume', 'adjfactor', 'weight'] 
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, df):
        volume = df['volume_preadj'][-350:]
        close = df['close_preadj'][-350:]
        temp1 = volume.copy(deep = True)
        con2 = close < close.shift(1)
        temp1[con2] = -1 * volume
        
        factor = bk.move_sum(temp1, 20, 10, axis = 0)[-330:]
        factor = bk.move_mean(factor, 20, 10, axis = 0)[-310:]

        w = df['weight'][-310:].values
        factor = factor * w
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 300, 150, axis = 0)[-10:]
        factor = np.nanmean(factor)
        
        return factor