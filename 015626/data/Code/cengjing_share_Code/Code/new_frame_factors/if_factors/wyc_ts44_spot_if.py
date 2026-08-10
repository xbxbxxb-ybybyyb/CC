from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_ts44_spot_if(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close','volume']}
    normalize_size = 5 * 242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None

    def calculate(self, df):
        temp1 = df['volume_000300.SH'][-65:]
        close = df['close_000300.SH'][-65:]
        con2 = close < close.shift(1)
        temp1[con2] = -1 * temp1
        factor = bk.move_sum(temp1, 25, 12, axis = 0)[-40:]
        factor = np.nanmean(factor)
        return factor
