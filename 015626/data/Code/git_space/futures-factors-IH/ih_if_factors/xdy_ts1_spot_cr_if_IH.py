from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class xdy_ts1_spot_cr_if_IH(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'high', 'stk_index_corr_sh50', 'adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[-1,0]'
    handle_preadj = True

    def calculate(self, df):
        high = df['high_preadj'][-235:].values
        close = df['close_preadj'][-235:].values
        high[abs(high) < 1e-8] = np.nan
        gain_high_60 = (high[60:] / high[:-60] - 1)[-175:]
        h_c = close / high - 1
        a = bk.move_mean(h_c, 60, 30, axis = 0)[-175:]
        a[abs(a) < 1e-8] = np.nan
        factor = bk.move_sum(gain_high_60 / a, 10, 5, axis = 0)[-165:]
        factor = -1 * bk.move_mean(factor, 10, 5, axis = 0)[-155:]

        cr = (2 * df['stk_index_corr_sh50'][-155:].rank(axis=1, pct=True) - 1).values
        factor = factor * cr
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 150, 75, axis = 0)[-5:]
        factor = np.nanmean(factor)
        
        return factor