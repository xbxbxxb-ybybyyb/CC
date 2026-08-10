from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_ts14_spot_if(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 5 * 242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.5,1]'
    handle_preadj = None 
    
    def calculate(self, df):
        close = df['close_000300.SH'][-150:]
        factor = np.where(close > close.shift(1), close.rolling(50, min_periods=25).std(), 0)[-100:]
        factor = ((bk.move_rank(factor, 60, 30, axis = 0) + 1) / 2)[-40:]
        factor = np.nanmean(factor)

        return factor