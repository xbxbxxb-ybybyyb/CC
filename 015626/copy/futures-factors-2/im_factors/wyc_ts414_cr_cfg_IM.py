from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd
        
class wyc_ts414_cr_cfg_IM(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'stk_index_corr_zz1000', 'adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, df):
        close = df['close_preadj'][-80:]
        factor = np.where(close > close.shift(2), close.rolling(50, min_periods = 25).std(), 0)

        factor = np.nanmean(factor[-30:], axis = 0)
        s = 2 * df['stk_index_corr_zz1000'][-1:].rank(axis = 1, pct=True) - 1
        factor = factor * s
        factor = np.nansum(factor, axis=1)
        
        return factor