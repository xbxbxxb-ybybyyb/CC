from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_ts44_future_vr(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'volume', 'adjfactor', 'stk_volatility'] 
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, df):
        volume = df['volume_preadj'][-145:]
        close = df['close_preadj'][-145:]
        temp1 = volume.copy(deep = True)
        con2 = close < close.shift(1)
        temp1[con2] = -1 * volume
        
        factor = bk.move_sum(temp1, 20, 10, axis = 0)[-125:]
        factor = bk.move_mean(factor, 20, 10, axis = 0)[-105:]

        vr = (2 * df['stk_volatility'][-105:].rank(axis=1, pct=True) - 1).values
        factor = factor * vr
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 100, 50, axis = 0)[-5:]
        factor = np.nanmean(factor)
        return factor