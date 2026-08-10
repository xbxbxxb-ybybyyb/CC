from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd


class wyc_ts14_spot_IH(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Index_Id'] = {'000016.SH':['close']}
    normalize_size = 0
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 

    def calculate(self, df):
        close = df['close_000016.SH'][-1403:]
        factor = np.where(close > close.shift(1), close.rolling(50, min_periods=25).std(), 0)[-1353:]
        factor = ((bk.move_rank(factor, 120, 60, axis = 0) + 1) / 2)[-1233:]
        factor = bk.move_mean(factor, 20, 10, axis = 0)[-1213:]
 
        factor = bk.move_rank(factor, 1210, 605, axis = 0)[-3:]
        factor = np.nanmean(factor)

        return factor