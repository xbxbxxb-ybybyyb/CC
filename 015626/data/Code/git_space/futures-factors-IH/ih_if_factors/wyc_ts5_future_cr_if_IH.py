from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

def get_delta(data, n):
    return data[n:] - data[:-n]

class wyc_ts5_future_cr_if_IH(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Stock'] = ['close','stk_index_corr_sh50','adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[0,1]'
    handle_preadj = True
    
    def calculate(self, df):

        N = 45
        close = df['close_preadj'][-1305:].values
        origin = get_delta((bk.move_sum(close, N,int(N/2), axis =0) / N), N) / close[:-N]
        change1 = -1 * (close - bk.move_min(close, N,int(N/2), axis =0))[N:]
        change2 = -1 * get_delta(close, 3)[N-3:]
        factor = np.where(origin<=0.05,change1,change2)[-1215:]

        factor = bk.move_rank(-1*factor, 1200, 600, axis = 0)[-15:]
        factor = np.nanmean(factor, axis = 0)

        cr = (2 * df['stk_index_corr_sh50'][-1:].rank(axis=1, pct=True) - 1)
        factor = factor * cr
        factor = np.nansum(factor, axis=1)
        
        return factor
