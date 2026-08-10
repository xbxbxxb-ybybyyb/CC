from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd


class wyc_ts14_future(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 4
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close']} 
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 

    def calculate(self, df):
        close = df['close_cont_IC'][-806:]
        factor = np.where(close > close.shift(2), close.rolling(50, min_periods=25).std(), 0)[-756:]
        factor = bk.move_mean(factor, 30, 15, axis = 0)[-726:]
        factor = bk.move_rank(factor, 726, 363, axis = 0)[-1]
        
        return factor