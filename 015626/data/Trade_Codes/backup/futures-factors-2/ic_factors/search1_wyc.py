from future_factor import FutureFactor
import pandas as pd
import numpy as np
import numpy.ma as ma
import bottleneck as bk

# mul2(sun_to_sn, long_short_ma_ratio(ts_std(sc, 25), 30, 100))
class search1_wyc(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Stock'] = ['SellUniqueOrderNum', 'SellTradeNum']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    
    def calculate(self, df):
        sun_to_sn = (df['SellUniqueOrderNum'][-1:].sum(axis = 1) / df['SellTradeNum'][-1:].sum(axis = 1)).values[-1]
        sc = df['close_000905.SH'][-125:]
        sc_std = sc.rolling(25, min_periods = 12).std().values[-100:]
        divnum = np.nanmean(sc_std)
        if divnum == 0:
            return np.nan
        else:
            return sun_to_sn * np.nanmean(sc_std[-30:]) / divnum