from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_ts4_icspot_if(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 2
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']} 
    normalize_size = 5 * 242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None
    
    def calculate(self, df):

        close = df['close_000905.SH'][-400:].values
        
        csum = bk.move_sum(close, 100, 50, axis = 0) / 100
        standard = (csum[100:] - csum[:-100]) / close[:-100]
        
        c1 = -1 * (close - bk.move_min(close, 100, 50, axis = 0))
        c2 = -1 * (close[3:] - close[:-3])
        factor = np.where(standard[-200:]<=0.05, c1[-200:], c2[-200:])
        factor = bk.move_rank(-1*factor, 100, 50, axis = 0)[-100:]
        factor = np.nanmean(factor)

        return factor
