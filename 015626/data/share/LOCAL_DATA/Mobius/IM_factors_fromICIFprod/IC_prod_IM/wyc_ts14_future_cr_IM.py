from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_ts14_future_cr_IM(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 2
    data_dict = dict()
    data_dict['Stock'] = ['close','adjfactor','stk_index_corr_zz1000'] 
    normalize_size = 5 * 242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True 

    def calculate(self, df):
        close = df['close_preadj'][-390:]
        factor = np.where(close > close.shift(2), close.rolling(50, min_periods=25).std(), 0)[-340:]
        factor = bk.move_mean(factor, 30, 15, axis = 0)[-310:]
        
        cr = (2 * df['stk_index_corr_zz1000'][-310:].rank(axis=1, pct=True) - 1).values
        factor = factor * cr
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 300, 150, axis = 0)[-10:]
        factor = np.nanmean(factor)

        return factor