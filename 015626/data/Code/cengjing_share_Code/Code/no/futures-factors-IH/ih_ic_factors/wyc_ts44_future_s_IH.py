from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd
    
class wyc_ts44_future_s_IH(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'volume', 'adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[0,1]'
    handle_preadj = True

    def calculate(self, df):
        volume = df['volume_preadj'][-40:]
        close = df['close_preadj'][-40:]
        temp1 = volume.copy(deep = True)
        con2 = close < close.shift(1)
        temp1[con2] = -1 * volume
        
        factor = bk.move_sum(temp1, 20, 10, axis = 0)[-20:]
        factor = np.nanmean(factor, axis = 0)

        factor = np.nansum(factor)

        return factor
