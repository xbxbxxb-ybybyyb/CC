from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class xdy_ts1_spot_ar_IH(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 2
    data_dict = dict()
    data_dict['Stock'] = ['close', 'high', 'amount', 'adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[-1,0.5]'
    handle_preadj = True
    
    def calculate(self, df):
        high = df['high_preadj'][-330:].values
        close = df['close_preadj'][-330:].values
        high[abs(high) < 1e-8] = np.nan
        gain_high_60 = (high[60:] / high[:-60] - 1)[-270:]
        h_c = close / high - 1
        a = bk.move_mean(h_c, 60, 30, axis = 0)[-270:]
        a[abs(a) < 1e-8] = np.nan
        factor = bk.move_sum(gain_high_60 / a, 10, 5, axis = 0)[-260:]
        factor = -1 * bk.move_mean(factor, 10, 5, axis = 0)[-250:]

        a = df['amount'][-250:]
        ar = (2 * a.rank(axis=1, pct=True) - 1).values
        factor = factor * ar
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 50, 25, axis = 0)[-200:]
        factor = np.nanmean(factor)

        return factor